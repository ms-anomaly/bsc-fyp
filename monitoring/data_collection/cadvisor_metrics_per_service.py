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

st_time = 1677659710
end_time = st_time + 5400
step = 5400
containers = ['user', 'dispatch', 'ratings', 'payment',  'mongodb', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
for container in containers:
    print(container)
    for i,st in enumerate(range(st_time,end_time,step)):
        print(st)
        # create a query string to select all data from a measurement
        query = f'from(bucket: "{bucket}") |> range(start: {st}, stop: {st+step}) \
                |> filter(fn: (r) => r._measurement == "prometheus_remote_write" and r.name == "robot-shop-{container}-1")\
                |> keep(columns:["_time","_value","_field"])\
                |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")'

        print("query: ",query)
        # create a query API client to execute the query
        query_api = client.query_api()
        csv_result = query_api.query_data_frame(org=org,query=query)

        # data = [record.values for table in results for record in table.records]
        # print('here2')
        # create a DataFrame from the query results
        df = pd.DataFrame(csv_result)
        out_dir = os.path.join(os.getcwd(),"data",now_time,str(i))
        if not os.path.exists(out_dir):
            print("making dir")
            os.makedirs(out_dir)

        df.to_csv(os.path.join(out_dir,container+ ".csv"),index=False)
        




