import glob
import pandas as pd

folder_path = 'D:/ACA/fyp/bsc-fyp/monitoring/data_collection/data/1677083237/'
files = glob.glob(folder_path+'*/*')
print(len(files))
total_hours = len(glob.glob(folder_path+'*'))
print('hours:',total_hours)



services = ['user', 'ratings', 'payment', 'shipping', 'mongo', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']

all =[]
for j,service in enumerate(services):
  data_service = []
  cols = []
  for i in range(0,total_hours):

    path = folder_path+str(i)+'/'+service+'.csv'        #change this accordingly
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    # print(path)
    # print(dataframe.shape)
    cols = df.columns
    

    data_service.extend(df.values.tolist())
    
  # for i in range(len(service_cols)):
  #   if not service_cols[i].startswith('container_'):
  #     service_cols[i] = service+'_'+service_cols[i]
  # service_cols.pop(0)
  # service_cols.insert(0,'timestamp')
  service_df = pd.DataFrame(data_service,columns=cols)
  all.append(service_df.shape)
  service_df.to_csv('anomaly_rt_delay_catalogue_rt_data_combined/'+service+'.csv')
print(all)
