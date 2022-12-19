import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


bucket = "robot-shop"
org = "fyp"
token = "SnvC2tu6nXOt0z3USH639fMlC1NkG9L_XJWVLA847tdC5DU2MbJgllFU6GRa1PCiBmvOc1q125hXrX680nD1aA=="
# Store the URL of your InfluxDB instance
url="http://0.0.0.0:8086"
measurement_name = "prometheus_remote_write"
container_names = ""

client = influxdb_client.InfluxDBClient(url,token,org)
query_api = client.query_api()

query = 'from(bucket:"robot-shop")\
|> range(start: -10m)\
|> filter(fn:(r) => r._measurement == "prometheus_remote_write")\
|> filter(fn:(r) => r.name == "robot-shop_cart_1")\
|> filter(fn:(r) => r._field == "container_memory_usage_bytes")'

result = query_api.query(org=org, query=query)

results = []
for table in result:
    # iterate through the tables
    for record in table.records:
        results.append((record.get_field(), record.get_value()))
    print(results)

    #break
print()
print(results)
