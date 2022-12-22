
from datetime import datetime, timedelta
import influxdb_client
import pandas as pd
import time
import os 
class query_generator:

    def __init__(self,client,bucket,measurement,container_names,fields):
        self.bucket = bucket
        self.container_names = container_names
        self.fields = fields
        #self.range = range
        self.measurement = measurement
        self.client = client
        
    def generate_query(self,container_name,field,start=-10,end=0,flag_first=False):
        '''
        This function needs to just generate a string
        '''
        if flag_first:
            query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: '+ str(start)+', stop: '+ str(end)+')\
            |> filter(fn:(r) => r._measurement == "'+self.measurement+'")\
            |> filter(fn:(r) => r.name == "'+container_name+'")\
            |> filter(fn:(r) => r._field == "'+field+'")\
            |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
            |> keep(columns:["time","_start","_stop","'+ field +'"])'
            
            return query
        query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: '+ str(start)+', stop: '+ str(end)+')\
            |> filter(fn:(r) => r._measurement == "'+self.measurement+'")\
            |> filter(fn:(r) => r.name == "'+container_name+'")\
            |> filter(fn:(r) => r._field == "'+field+'")\
            |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
            |> keep(columns:["'+ field +'"])'

        print(start,end)
        return query

    def get_csv(self,range_st,range_end,window_size=3600):
        org = "fyp"
        results = []
        now_time = str(int(time.time()))
        # iterate over time to generate dataframes for windows of time
        for c,window in enumerate(range(range_st,range_end,window_size)):
            start = range_st + c * window_size
            end = start + window_size
            for container in self.container_names:
                container_window_df = pd.DataFrame()
                for i,field in enumerate(self.fields):
                    query = ''
                    if (i == 0):
                        # set up time in dataframe
                        query = self.generate_query(container,field,start,end,True)
                    #end = range_st + window_size
                    else:
                        query = self.generate_query(container,field,start,end)
                    res = self.client.query_df(query)
                    print(res.head())
                    # append res to data
                    container_window_df = pd.concat([container_window_df,res],axis=1)
                    
                out_dir = os.path.join(os.getcwd(),"data",now_time,str(c))
                if not os.path.exists(out_dir):
                    print("making dir")
                    os.makedirs(out_dir)
                container_window_df.to_csv(os.path.join(out_dir,container+ ".csv"))
             



class influx_data_client:
    def __init__(self,url,token,org):
        self.client = influxdb_client.InfluxDBClient(url,token,org)
        self.query_api = self.client.query_api()
        self.org=org
    def query_df(self,query):
        #result = self.query_api.query(org=org, query=query)
        result = self.query_api.query_data_frame(org=self.org,query=query)
        # results = []
        # for table in result:
        #     for record in table.records:
        #         results.append((record.get_field(), record.get_value()))
        #
        #print(result.to_string())
        return result

bucket = "robot-shop"
org = "fyp"
token = "SnvC2tu6nXOt0z3USH639fMlC1NkG9L_XJWVLA847tdC5DU2MbJgllFU6GRa1PCiBmvOc1q125hXrX680nD1aA=="
# Store the URL of your InfluxDB instance
url="http://0.0.0.0:8086"
measurement_name = "prometheus_remote_write"
containers = ["robot-shop_cart_1","robot-shop_catalogue_1"]
fields = ["container_memory_usage_bytes","container_cpu_usage_seconds_total"]
end_time = int(time.time())
st_time = 1671398743
client = influx_data_client(url,token,org)
query_gen = query_generator(client,bucket,measurement_name,containers,fields)
query_gen.get_csv(st_time,end_time)




