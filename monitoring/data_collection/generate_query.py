
from datetime import datetime, timedelta
import pandas as pd

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

    def iterate_range(self,range_st,range_end,window_size=3600):
        results = []
        for container in self.container_names:
            for field in self.fields:
                end = range_st + window_size
                query = self.generate_query(container,field,range_st,end)




class influx_data_client:
    def __init__(self,url,token,org):
        self.client = influxdb_client.InfluxDBClient(url,token,org)
        self.query_api = self.client.query_api()
    
    def query(self,query):
        #result = self.query_api.query(org=org, query=query)
        result = self.query_api.query_data_frame(query=query)
        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
        return results



