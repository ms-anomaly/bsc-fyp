import glob
import pandas as pd

folder_path = 'D:/ACA/fyp/bsc-fyp/monitoring/data_collection/data/anomaly_rt_delay_catalogue_cadvisor_data/'
files = glob.glob(folder_path+'*/*')
print(len(files))
total_hours = len(glob.glob(folder_path+'*'))
print('hours:',total_hours)
services = ['user', 'dispatch', 'ratings', 'payment', 'shipping', 'mongodb', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
drop_cols = ['container_last_seen','container_spec_cpu_period',	'container_spec_cpu_shares',	'container_spec_memory_limit_bytes',	'container_spec_memory_reservation_limit_bytes',	'container_spec_memory_swap_limit_bytes',	'container_start_time_seconds']
# Update row number of last available datapoint in last hour
last_row = 722
for j,service in enumerate(services):
  data_service = []
  service_cols = []
  for i in range(0,total_hours):
    if i==(total_hours-1):skiprows=last_row
    else :skiprows=722

    path = folder_path+str(i)+'/'+service+'.csv'        #change this accordingly
    data = pd.read_csv(path)
    dataframe = pd.DataFrame(data)
    cols = ['_time']
    cols +=  [col for col in dataframe.columns if (col.startswith('container_') and (col not in drop_cols))] 
    df = dataframe.loc[:, cols]
    size = df.shape
    print(path)
    print('size: ',size)
    df['_time'] = pd.to_datetime(df['_time'])

    max_timestamp = df['_time'][0]
    for i, row in df.iterrows():
        if row['_time'] < max_timestamp:
            df = df.iloc[:i]
            break
        max_timestamp = row['_time']

    df = df.fillna(method='ffill')

    data_service.extend(df.values.tolist())
    service_cols = cols

  for i in range(len(service_cols)):
    if not service_cols[i].startswith('container_'):
      service_cols[i] = service+'_'+service_cols[i]
  service_cols.pop(0)
  service_cols.insert(0,'timestamp')
  service_df = pd.DataFrame(data_service,columns=service_cols)
  service_df.to_csv('anomaly_rt_delay_catalogue_cadvisor_data_combined/'+service+'.csv')

