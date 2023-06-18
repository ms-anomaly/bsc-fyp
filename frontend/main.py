import http.client
import datetime
import time
import datetime
import requests
import json
import random

import torch
import torch.nn as nn
import numpy as np
import pandas

import const
import prom
import frontend
import localization
from localization import *
import matplotlib.pyplot as plt

mean_train = pandas.read_csv("model/mean.csv")
mean_train.pop(mean_train.columns[0])
# print(mean_train.pop(mean_train.columns[0]).head)
std_train = pandas.read_csv("model/std_d.csv")
std_train.pop(std_train.columns[0])

mean_train_t = torch.tensor(mean_train.values)
std_train_t = torch.tensor(std_train.values)

# print("mean shape:", mean_train_t.shape)
# print("std shape:", std_train_t.shape)

heatmap = np.zeros((12,22))
plt.imshow(heatmap)
plt.title("SHAP Value Heat Map")
plt.savefig("plots/heatmap.png")

node_colors = dict.fromkeys(const.services, 'lightgreen')
frontend.drawServiceGraph(const.adj_matrix, const.services, node_colors, 'plots/serviceGraph.png')

if __name__ == "__main__":
    while True:
        ######################################
        ##### Poll data from Prometheus ######
        ######################################

        data3D = prom.getData()
        data_instance = data3D - mean_train_t
        data_instance = data3D / std_train_t

        # sampleDataNew = [[[1] * 22] * 12] * 24

        ######################################
        ####### Send request to Bento ########
        ######################################

        response = requests.post(
            prom.BENTOML + 'classify', 
            data=json.dumps(data_instance.tolist()),
            headers={"content-type":"application/json"}
        )

        results = response.json()
        # print(results)

        ######################################
        ####### Calculate SHAP Values ########
        ######################################

        anomalyNo = 0
        for i in results:
            if i[0]>=3.51:
                anomalyNo += 1
        
        if anomalyNo>3:
            sig = nn.Sigmoid()
            # model = "model/explainer.pkl"
            localizer = localization.Localize(sig)
            
            suspect_services, suspect_features = localizer.localize_anomaly_voting(data_instance.to(torch.float32) , torch.tensor(results).to(torch.float32))

            print(suspect_services)
            print(suspect_features)
            print(const.services[suspect_services[-1]])
            print(const.cols_with_rt[suspect_features[-1]])

            ######################################
            ####### Output to front-end ########
            ######################################

            node_colors = dict.fromkeys(const.services, 'lightgreen')
            node_colors[const.services[suspect_services[-1]]] = 'red'
            node_colors[const.services[suspect_services[-2]]] = 'mistyrose'
            node_colors[const.services[suspect_services[-3]]] = 'orange'

            print(node_colors)
            #DEBUG
            print("Found anomalies")

            frontend.drawServiceGraph(const.adj_matrix, const.services, node_colors, 'plots/serviceGraph.png')
        else:
            node_colors = dict.fromkeys(const.services, 'lightgreen')
            frontend.drawServiceGraph(const.adj_matrix, const.services, node_colors, 'plots/serviceGraph.png')
            #DEBUG
            print("No anomalies")



        time.sleep(10)        
