import glob
import pandas as pd

folder_path = '/data/1676718915/'
files = glob.glob(folder_path+'*/*')
total_hours = len(glob.glob(folder_path+'*'))

services = set()
for file in files:
  service = file.split('robot-shop_')[1][:-6]
  services.add(service)

services=list(services)
# Update row number of last available datapoint in last hour
last_row = 585
for j,service in enumerate(services):
  data_service = []
  service_cols = []
  for i in range(0,total_hours):
    if i==(total_hours-1):skiprows=last_row
    else :skiprows=720

    path = folder_path+str(i)+'/robot-shop_'+service+'_1.csv'
    data = pd.read_csv(path, nrows=skiprows)
    dataframe = pd.DataFrame(data)
    cols = ['_time','container_cpu_system_seconds_total','container_cpu_user_seconds_total','container_memory_usage_bytes', 'container_memory_working_set_bytes']
    cols +=  [col for col in dataframe.columns if col.startswith('rt_')] 
    df = dataframe.loc[:, cols]
    data_service.extend(df.values.tolist())
    service_cols = cols
  for i in range(len(service_cols)):
    if not service_cols[i].startswith('rt_'):
      service_cols[i] = service+'_'+service_cols[i]
  service_cols.pop(0)
  service_cols.insert(0,'timestamp')
  service_df = pd.DataFrame(data_service,columns=service_cols)
  service_df.to_csv(service+'.csv')