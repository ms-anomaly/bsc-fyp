
from datetime import datetime, timedelta
import pandas as pd
import time

class query_generator:

    def __init__(self,client,bucket,measurement,container_names,fields):
        self.bucket = bucket
        self.container_names = container_names
        self.fields = fields
        #self.range = range
        self.measurement = measurement
        self.client = client
        
    def generate_query(self,container_name,field,start=-10,end=0):
        '''
        This function needs to just generate a string
        '''
        query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: '+ str(start)+', end: '+ str(end)+')\
            |> filter(fn:(r) => r._measurement == "'+self.measurement+'")\
            |> filter(fn:(r) => r.name == "'+container_name+'")\
            |> filter(fn:(r) => r._field == "'+field+'")'
        return query

    def get_csv(self,range_st,range_end,window_size=3600):
        results = []
        # iterate over time to generate dataframes for windows of time
        for window in range (range_st,range_end,window_size):
            start = range_st + window * window_size
            end = start + window_size
            for container in self.container_names:
                container_window_df = pd.DataFrame()
                for field in self.fields:
                    end = range_st + window_size
                    query = self.generate_query(container,field,start,end)
                    res = self.client.query_df(query)
                    # append res to data
                    pd.concat(container_window_df,res,axis=1)
                container_window_df.to_csv("./data/" + str(int(time.time())) + window +"/"+ container + ".csv")
             



class influx_data_client:
    def __init__(self,url,token,org):
        self.client = influxdb_client.InfluxDBClient(url,token,org)
        self.query_api = self.client.query_api()
    
    def query_df(self,query):
        #result = self.query_api.query(org=org, query=query)
        result = self.query_api.query_data_frame(query=query)
        # results = []
        # for table in result:
        #     for record in table.records:
        #         results.append((record.get_field(), record.get_value()))
        #
        print(result.to_string())
        return result

bucket = "robot-shop"
org = "fyp"
token = "SnvC2tu6nXOt0z3USH639fMlC1NkG9L_XJWVLA847tdC5DU2MbJgllFU6GRa1PCiBmvOc1q125hXrX680nD1aA=="
# Store the URL of your InfluxDB instance
url="http://0.0.0.0:8086"
measurement_name = "prometheus_remote_write"
containers = ["robot-shop_cart_1",]
fields = ["container_memory_usage_bytes",""]
client = influx_data_client(url,token,org)
query_gen = query_generator(client,bucket,measurement_name,containers,fields)



