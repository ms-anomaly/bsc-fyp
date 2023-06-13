import http.client
import datetime
import time
import datetime
import requests
import json
import random
import shap
import pickle
import numpy as np
import const
import prom
#import frontend
import pickle
from shap import DeepExplainer
import pandas as pd
import torch
import numpy
import torch.nn as nn
import torch.nn.functional as F

# class definitions
class GATLayer(nn.Module):
    
    def __init__(self, c_in, c_out, num_heads=1, concat_heads=True, alpha=0.2):
        """
        Inputs:
            c_in - Dimensionality of input features
            c_out - Dimensionality of output features
            num_heads - Number of heads, i.e. attention mechanisms to apply in parallel. The 
                        output features are equally split up over the heads if concat_heads=True.
            concat_heads - If True, the output of the different heads is concatenated instead of averaged.
            alpha - Negative slope of the LeakyReLU activation.
        """
        super().__init__()
        self.num_heads = num_heads
        self.concat_heads = concat_heads
        if self.concat_heads:
            assert c_out % num_heads == 0, "Number of output features must be a multiple of the count of heads."
            c_out = c_out // num_heads
        
        # Sub-modules and parameters needed in the layer
        self.projection = nn.Linear(c_in, c_out * num_heads)
        self.a = nn.Parameter(torch.Tensor(num_heads, 2 * c_out)) # One per head
        self.leakyrelu = nn.LeakyReLU(alpha)
        
        # Initialization from the original implementation
        nn.init.xavier_uniform_(self.projection.weight.data, gain=1.414)
        nn.init.xavier_uniform_(self.a.data, gain=1.414)
        
    def forward(self, node_feats, adj_matrix, print_attn_probs=False):
        """
        Inputs:
            node_feats - Input features of the node. Shape: [batch_size, c_in]
            adj_matrix - Adjacency matrix including self-connections. Shape: [batch_size, num_nodes, num_nodes]
            print_attn_probs - If True, the attention weights are printed during the forward pass (for debugging purposes)
        """
        batch_size, num_nodes = node_feats.size(0), node_feats.size(1)
        
        # Apply linear layer and sort nodes by head
        node_feats = self.projection(node_feats)
        node_feats = node_feats.view(batch_size, num_nodes, self.num_heads, -1)
        # We need to calculate the attention logits for every edge in the adjacency matrix 
        # Doing this on all possible combinations of nodes is very expensive
        # => Create a tensor of [W*h_i||W*h_j] with i and j being the indices of all edges
        edges = adj_matrix.nonzero(as_tuple=False) # Returns indices where the adjacency matrix is not 0 => edges
        node_feats_flat = node_feats.view(batch_size * num_nodes, self.num_heads, -1)
        edge_indices_row = edges[:,0] * num_nodes + edges[:,1]
        edge_indices_col = edges[:,0] * num_nodes + edges[:,2]
        a_input = torch.cat([
            torch.index_select(input=node_feats_flat, index=edge_indices_row, dim=0),
            torch.index_select(input=node_feats_flat, index=edge_indices_col, dim=0)
        ], dim=-1) # Index select returns a tensor with node_feats_flat being indexed at the desired positions along dim=0
        # Calculate attention MLP output (independent for each head)
        attn_logits = torch.einsum('bhc,hc->bh', a_input, self.a) 
        attn_logits = self.leakyrelu(attn_logits)
        # Map list of attention values back into a matrix
        attn_matrix = attn_logits.new_zeros(adj_matrix.shape+(self.num_heads,)).fill_(-9e15)
        attn_matrix[adj_matrix[...,None].repeat(1,1,1,self.num_heads) == 1] = attn_logits.reshape(-1)
        # Weighted average of attention
        self.attn_probs = F.softmax(attn_matrix, dim=2)
        if print_attn_probs:
            print("Attention probs\n", self.attn_probs.permute(0, 3, 1, 2))
        node_feats = torch.einsum('bijh,bjhc->bihc', self.attn_probs, node_feats)
        # If heads should be concatenated, we can do this by reshaping. Otherwise, take mean
        if self.concat_heads:
            node_feats = node_feats.reshape(batch_size, num_nodes, -1)
        else:
            node_feats = node_feats.mean(dim=2)
        return node_feats 

class gat_lstm_autoencoder(nn.Module):
  def __init__(self, num_nodes,input_features_size, gat_out_size, lstm_out_size, linear_out_size, reconstruct_hidden_size1, reconstruct_hidden_size2, num_layers, num_heads,batch_size,period):

    super(gat_lstm_autoencoder, self).__init__()


    self.num_nodes = num_nodes
    self.hidden_size = gat_out_size
    self.hidden_size1 = lstm_out_size
    self.input_features_size = input_features_size
    self.batch_size = batch_size
    self.period = period
    self.gat = GATLayer(input_features_size, 16, num_heads)
    self.gat1 = GATLayer(16, 12, num_heads)
    # self.gat2 = GATLayer(16, 12, num_heads)

    self.lstm = nn.LSTM(num_nodes*12, 12*12, 2, batch_first=False, dropout=0.25) #24
    self.lstm1 = nn.LSTM(num_nodes*12, 12*12, 2, batch_first=False, dropout=0.25) #12
    # self.lstm2 = nn.LSTM(num_nodes*8, 12*8, 2, batch_first=False, dropout=0.25) #6
    # self.lstm3 = nn.LSTM(num_nodes*8, 12*8, 2, batch_first=False, dropout=0.25) #12
    # self.lstm4 = nn.LSTM(num_nodes*8, 12*8, 2, batch_first=False, dropout=0.25) #24

    self.gat3 = GATLayer(12, 16, num_heads)
    self.gat4 = GATLayer(16, 24, num_heads)
    self.fc_layers = nn.Sequential(
        nn.Linear(12*24, 12*input_features_size),
        nn.LeakyReLU()
    )

    self.linear = nn.Linear( 12*24, 12*input_features_size)
    # self.linear1 = nn.Linear( 12*16, 12*input_features_size)
    # self.linear2 = nn.Linear( 12*24, 12*20)
    # self.linear2 = nn.Linear( 12*10, 12*20)

    self.dropout = nn.Dropout(p=0.3)
    self.dropout1 = nn.Dropout(p=0.3)
    self.dropout2 = nn.Dropout(p=0.3)
    # self.dropout3 = nn.Dropout(p=0.3)

    self.leakyrelu = nn.ReLU(0.2)

    self.norm = nn.LayerNorm(12*8) 
    self.norm1 = nn.LayerNorm(12*16)
    self.norm2 = nn.LayerNorm(12*input_features_size) 
    self.adj = torch.tensor([#['payment 0', 'shipping 1', 'redis 2', 'mongodb 3', 'dispatch 4', 'rabbitmq 5', 'user 6', 'mysql 7', 'catalogue 8', 'ratings 9', 'web 10', 'cart 11']
       [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
        [1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1]]])
    
    # self.norm3 = nn.LayerNorm(12*10)
    # self.norm4 = nn.LayerNorm(12*15)
    # self.norm5 = nn.LayerNorm(12*20)
    # self.reconstruct = ReconstructionModel(linear_out_size,reconstruct_hidden_size1, reconstruct_hidden_size2,num_nodes*input_features_size)

  # GAT:    [batch_size,num_nodes,features],[num_nodes,num_nodes]   |   [batch_size,num_nodes,hidden_size]
  # LSTM:   [batch_size,1,num_nodes*hidden_size]                    |   [batch_size,1,num_nodes*hidden_size1]
  # Linear: [batch_size,num_nodes*hidden_size1]                     |   [batch_size,num_nodes*hidden_size2]
  # Recons: [batch_size,num_nodes*hidden_size2]                     |   [batch_size,num_nodes*input_size]
 
  
    
  def forward(self, x):
    INP = x
    batch_size = x.size(0)
    # print('before_gat',x.shape)
    x = self.gat(x, self.adj)
    x = F.elu(x)
    # x = self.leakyrelu(x)
    x = self.gat1(x, self.adj)
    x = F.elu(x)
    # x = self.leakyrelu(x)
    # x = self.gat2(x, self.adj)
    # # x = F.elu(x)
    # x = self.leakyrelu(x)
    gat_out = x

    # print('after_gat',x.shape)
    #x = x.reshape(self.period,batch_size//self.period,self.num_nodes*12)
    x = x.reshape(self.period,-1,self.num_nodes*12)
    x = self.dropout(x)
    # print('before_lstm',x.shape)
    x,(hn,cn) = self.lstm(x)
    decoder_hidden = (hn, torch.zeros_like(hn))
    decoder_input = torch.zeros_like(x)
    encoder_out = x
    x,(hn,cn) = self.lstm1(decoder_input,decoder_hidden)
    
    x = x.reshape(-1,self.num_nodes,12)
    x = self.gat3(x, self.adj)
    x = F.elu(x)
    # x = self.leakyrelu(x)
    x = self.gat4(x, self.adj)
    x = F.elu(x)
    # x = self.leakyrelu(x)

    # x,(hn,cn) = self.lstm2(x[-6:])
    
    # x,(hn,cn) = self.lstm3(torch.cat((x,x),0))
    # x,(hn,cn) = self.lstm4(torch.cat((x,x),0))
    # x = self.norm(x)
    
    
    
    
    x = x.reshape(batch_size,self.num_nodes*24)
    #x = self.linear(x)
    #x = self.leakyrelu(x)
    x = self.fc_layers(x)
    # x = self.dropout1(x)
    
    # x = self.norm1(x)
    
    # x = self.linear1(x)
    # x = self.leakyrelu(x)
    # # x = self.dropout2(x)
    # x = self.norm2(x)

    x_ = x.reshape(batch_size,self.num_nodes,-1)
    out = torch.stack([F.mse_loss(INP[i], x_[i],reduce = 'sum') for i in range(x.shape[0])])
    out = out.reshape([-1,1])
    # x_ = x
    return out#x_,x,gat_out,encoder_out


num_nodes = 12
period = 24

num_heads = 4 # number of GAT heads
input_features_size = 22
gat_out_size = 24 

lstm_out_size = 20*num_nodes #20*12
num_layers = 4 # number of LSTM layers

linear_out_size = 256 # 24*12
reconstruct_hidden_size1 = 128
reconstruct_hidden_size2 = 64

num_epochs = 20 # number of training epochs
batch_size = 504 # size of each training batch

# model = gat(num_nodes,input_features_size,gat_out_size,lstm_out_size,linear_out_size,reconstruct_hidden_size1,reconstruct_hidden_size2,num_layers,num_heads,batch_size,period)
# def __init__( num_nodes,input_features_size, hidden_size, hidden_size1, hidden_size2, reconstruct_hidden_size1, reconstruct_hidden_size2, num_layers, num_heads,batch_size,period):


# end class definitions

services = ['payment', 'shipping', 'redis', 'mongodb', 'dispatch', 'rabbitmq', 'user', 'mysql', 'catalogue', 'ratings', 'web', 'cart']
anomalies = ['rt-delay-catalogue', 'packetloss-user', 'low-bandwidth-user', 'high-cpu-dispatch', 'high-latency-user-2', 'high-load-1500',
 'out-of-order-packets-user-2', 'high-latency-user', 'service-down-payment', 'out-of-order-packets-user', 'packetloss-user-2', 
 'high-fileIO-payment', 'memory-leak-cart']

cumulative_cols = ['container_cpu_system_seconds_total',
'container_cpu_usage_seconds_total',
'container_cpu_user_seconds_total',
'container_network_receive_bytes_total',
'container_network_receive_errors_total',
'container_network_receive_packets_dropped_total',
'container_network_receive_packets_total',
'container_network_transmit_bytes_total',
'container_network_transmit_errors_total'	,
'container_network_transmit_packets_dropped_total',
'container_network_transmit_packets_total',
'container_fs_io_time_seconds_total',
'container_memory_failures_total',
'container_memory_failcnt',
'container_fs_write_seconds_total']

other_cols = ['container_fs_usage_bytes',
'container_memory_rss',
'container_memory_usage_bytes',
'container_memory_working_set_bytes']
cols = other_cols + cumulative_cols
cols_with_rt = cols + ['sum','ma','ma20']


class Localize():
  def __init__(self,sigmoid_func,threshold=3.5):
    num_nodes = 12
    period = 24

    num_heads = 4 # number of GAT heads
    input_features_size = 22
    gat_out_size = 24 

    lstm_out_size = 20*num_nodes #20*12
    num_layers = 4 # number of LSTM layers

    linear_out_size = 256 # 24*12
    reconstruct_hidden_size1 = 128
    reconstruct_hidden_size2 = 64

    num_epochs = 30 # number of training epochs
    batch_size = 504 # size of each training batch
    num_nodes = 12
    period = 24

    num_heads = 4 # number of GAT heads
    input_features_size = 22
    gat_out_size = 24 

    lstm_out_size = 20*num_nodes #20*12
    num_layers = 4 # number of LSTM layers

    linear_out_size = 256 # 24*12
    reconstruct_hidden_size1 = 128
    reconstruct_hidden_size2 = 64

    num_epochs = 30 # number of training epochs
    batch_size = 504 # size of each training batch

    model = gat_lstm_autoencoder(num_nodes,input_features_size,gat_out_size,lstm_out_size,linear_out_size,reconstruct_hidden_size1,reconstruct_hidden_size2,num_layers,num_heads,batch_size,period)


    self.explainer = DeepExplainer(model,torch.ones([24,12,22]))
    file = open('model/explainer_30_epoch.pkl', 'rb')
    self.explainer = pickle.load(file)
    self.sig = sigmoid_func
    self.threshold = threshold

  def localize_anomaly(self,period,predictions):
    # period = [24,12,22] input data tensor
    # predictions = [24] predictions tensor  eg [5.6,2,7,8.9,10,1,9,1.9,0.2,...]
    predictions = predictions.squeeze()
    results = self.sig(predictions-self.threshold)
    b = results > self.threshold
    detected_anom_timesteps = b.nonzero().squeeze()
    print(results.shape)
    print(b.shape)
    print(detected_anom_timesteps.shape)
    
    shap_values = self.explainer.shap_values(period)
    shap_values = np.stack(shap_values, axis=0)
    shap_vals_cpy = shap_values
    heat_maps_per_timestep = np.stack([shap_vals_cpy[i]/shap_vals_cpy[i].sum() for i in range(shap_vals_cpy.shape[0])])
    print(heat_maps_per_timestep.shape)
    # get shap values of detected anomalies
    shap_values_of_detected_anomalies = heat_maps_per_timestep[detected_anom_timesteps].squeeze()
    print(shap_values_of_detected_anomalies.shape)
    # sum features of all detected anomalies
    sum_shap_values  = np.sum(shap_values_of_detected_anomalies,axis=0)
    print(sum_shap_values.shape)
    # aggregate over features to find the anomalous node
    sum_services_shap_values  = np.sum(np.fabs(sum_shap_values),axis=1)
    print(sum_services_shap_values.shape)
    top_4_anom_service =  sum_services_shap_values.argsort()[-4:] # Get top 4 because each service is dependent on at most 4 other services
    print("top 4 anom services ",top_4_anom_service)
    feature_id = [np.fabs(sum_shap_values)[service_ids,:].argsort()[-1] for service_ids in top_4_anom_service]
    return top_4_anom_service, feature_id

# if __name__ == "__main__":
#     # TESTING CODE

#     # USE LOADED MODEL HERE.
#     model = gat_lstm_autoencoder(num_nodes,input_features_size,gat_out_size,lstm_out_size,linear_out_size,reconstruct_hidden_size1,reconstruct_hidden_size2,num_layers,num_heads,batch_size,period)
#     explainer = DeepExplainer(model,torch.ones([24,12,22]))
#     file = open('explainer.pkl', 'rb')
#     explainer = pickle.load(file)
#     threshold = 3.5
#     sig = nn.Sigmoid()

#     anom_instances_df = pd.read_csv("anom_data_instances.csv",index_col=False)
#     anom_instances_df.pop(anom_instances_df.columns[0])
#     print(anom_instances_df.head())
#     anom_instances = torch.tensor(anom_instances_df.values)
#     anom_instances =anom_instances.reshape(-1,12,22)
#     print(anom_instances.shape)

#     localizer = Localize(model,sig)
#     suspect_services, suspect_features = localizer.localize_anomaly(anom_instances[:24,:,:].to(torch.float32),torch.Tensor([5]*24))
#     for c,x in enumerate(suspect_services):
#         print(services[x], cols_with_rt[suspect_features[c]])


