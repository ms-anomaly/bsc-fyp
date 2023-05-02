from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import os
import time
token = 'amcAeToLou5FOnvhv8czQYOfD_2fMIx2MjiUyZgpLBoRsXh0_HNQr1-i-hB92OsFeSH6nnhcoDeaVxiaCQLbSw=='
org = "fyp"
# create a client to connect to the InfluxDB 2.0 server
client = InfluxDBClient(url="http://10.8.100.247:8086", token=token, org=org,timeout=300_000)
now_time = str(int(time.time()))
# select the bucket to use
bucket = "robot-shop"

### Change these for each anomaly
anomaly = 'high_cpu' 
st_time = 1683007200
end_time = st_time+30000
step = 6000
anomaly_services = ['ratings','cart','user','payment','dispatch']

containers = ['user', 'dispatch','payment', 'ratings', 'shipping',  'mongodb', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
for i,anomaly_serivce in enumerate(anomaly_services):
    print(anomaly_serivce)
    anomaly_st = st_time + i*step
    anomaly_end = anomaly_st + step
    save_path = anomaly+'_'+anomaly_serivce+'_cadvisor'
    for container in containers:
    
        print(anomaly_st)
        query = f'from(bucket: "{bucket}") |> range(start: {anomaly_st}, stop: {anomaly_end}) \
                |> filter(fn: (r) => r._measurement == "prometheus_remote_write" and r.name == "robot-shop-{container}-1")\
                |> keep(columns:["_time","_value","_field"])\
                |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")'

        print("query: ",query)
        # create a query API client to execute the query
        query_api = client.query_api()
        csv_result = query_api.query_data_frame(org=org,query=query)

        df = pd.DataFrame(csv_result)
        max_timestamp = pd.Timestamp(st_time,unit='s',tz='+00:00')
        for j, row in df.iterrows():
            if row['_time'] < max_timestamp:
                df = df.iloc[:j]
                break
            max_timestamp = row['_time']
        out_dir = os.path.join(os.getcwd(),"data",save_path)
        if not os.path.exists(out_dir):
            print("making dir")
            os.makedirs(out_dir)

        df.to_csv(os.path.join(out_dir,container+ ".csv"),index=False)
        




