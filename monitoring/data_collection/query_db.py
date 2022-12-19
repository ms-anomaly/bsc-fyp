import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

class influx_data_client:
    def __init__(self,url,token,org):
        self.client = influxdb_client.InfluxDBClient(url,token,org)
        self.query_api = self.client.query_api()
    
    def query(self,query):
        result = self.query_api.query(org=org, query=query)
        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
        return results



bucket = "robot-shop"
org = "fyp"
token = "SnvC2tu6nXOt0z3USH639fMlC1NkG9L_XJWVLA847tdC5DU2MbJgllFU6GRa1PCiBmvOc1q125hXrX680nD1aA=="
# Store the URL of your InfluxDB instance
url="http://0.0.0.0:8086"
measurement_name = "prometheus_remote_write"
container_names = "robot-shop_cart_1"

#client = influxdb_client.InfluxDBClient(url,token,org)
#query_api = client.query_api()

query = 'from(bucket:"'+bucket+'")\
|> range(start: -10m)\
|> filter(fn:(r) => r._measurement == "'+measurement_name+'")\
|> filter(fn:(r) => r.name == "'+container_names+'")\
|> filter(fn:(r) => r._field == "container_memory_usage_bytes")'

data_client = influx_data_client(url,token,org)
result = data_client.query(query)
print(result)
#result = query_api.query(org=org, query=query)

#results = []
#for table in result:
#    # iterate through the tables
#    for record in table.records:
#        results.append((record.get_field(), record.get_value()))
#    print(results)

    #break
#print()
#print(results)
