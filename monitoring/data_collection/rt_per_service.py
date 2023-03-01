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
# containers = ['user', 'dispatch', 'ratings', 'payment', 'shipping', 'mongo', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
containers = ['user', 'dispatch', 'ratings', 'payment', 'shipping', 'mongo', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
metrics = ['rt_ratings_put_PDO_count', 'rt_ratings_put_PDO_sum', 'rt_payment_delete_cart_count', 'rt_payment_delete_cart_sum', 'rt_cart_get_catalogue_count', 'rt_cart_get_catalogue_sum', 'rt_ratings_get_catalogue_count', 'rt_ratings_get_catalogue_sum', 'rt_catalogue_get_mongo_categories_count', 'rt_catalogue_get_mongo_categories_sum', 'rt_catalogue_get_mongo_products_count', 'rt_catalogue_get_mongo_products_sum', 'rt_catalogue_get_mongo_productscat_count', 'rt_catalogue_get_mongo_productscat_sum', 'rt_catalogue_get_mongo_productsku_count', 'rt_catalogue_get_mongo_productsku_sum', 'rt_catalogue_get_mongo_search_count', 'rt_catalogue_get_mongo_search_sum', 'rt_user_get_mongo_checkid_count', 'rt_user_get_mongo_checkid_sum', 'rt_user_get_mongo_history_count', 'rt_user_get_mongo_history_sum', 'rt_user_get_mongo_users_count', 'rt_user_get_mongo_users_sum', 'rt_user_post_mongo_login_count', 'rt_user_post_mongo_login_sum', 'rt_user_post_mongo_order_count', 'rt_user_post_mongo_order_sum', 'rt_user_post_mongo_register_count', 'rt_user_post_mongo_register_sum', 'rt_web_post_payment_count', 'rt_web_post_payment_sum', 'rt_dispatch_get_rabbitmq_count', 'rt_dispatch_get_rabbitmq_sum', 'rt_web_get_ratings_count', 'rt_web_get_ratings_sum', 'rt_cart_delete_redis_count', 'rt_cart_delete_redis_sum', 'rt_cart_get_redis_count', 'rt_cart_get_redis_sum', 'rt_cart_post_redis_count', 'rt_cart_post_redis_sum', 'rt_user_get_redis_count', 'rt_user_get_redis_sum', 'rt_web_get_shipping_calcid_seconds_count', 'rt_web_get_shipping_calcid_seconds_sum', 'rt_web_get_shipping_code_seconds_count', 'rt_web_get_shipping_code_seconds_sum', 'rt_web_get_shipping_postconfirm_seconds_count', 'rt_web_get_shipping_postconfirm_seconds_sum', 'rt_payment_get_user_count', 'rt_payment_get_user_sum', 'rt_payment_post_user_count', 'rt_payment_post_user_sum']
services = dict()
for i in containers:
    services[i] = []
for metric in metrics:
    callee = metric.split('_')[3]
    if callee=='PDO': callee='mysql'
    
    services[callee].append(metric)
containers = ['user', 'dispatch', 'ratings', 'payment', 'mongo', 'web', 'cart', 'redis', 'mysql', 'rabbitmq', 'catalogue']
for service in containers:
    data_service = []
    for i,st in enumerate(range(st_time,end_time,step)):
    
        dfs = []
        flag = True
        for metric_name in services[service]:
            print(st)
            # create a query string to select all data from a measurement
            query = f'from(bucket: "{bucket}") |> range(start: {st}, stop: {st+step}) \
                    |> filter(fn: (r) => r._measurement == "prometheus_remote_write" and r._field == "{metric_name}")\
                    |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
                    |> keep(columns:["_time","{metric_name}"])'
                    
            print("query: ",query)
            # create a query API client to execute the query
            query_api = client.query_api()
            csv_result = query_api.query_data_frame(org=org,query=query)

            # data = [record.values for table in results for record in table.records]
            # print('here2')
            # create a DataFrame from the query results
            df = pd.DataFrame(csv_result)
            max_timestamp = pd.Timestamp(st_time,unit='s',tz='+00:00')
            for j, row in df.iterrows():
                if row['_time'] < max_timestamp:
                    df = df.iloc[:j]
                    break
                max_timestamp = row['_time']
            df = df.fillna(method='ffill')
            if flag: 
                flag = False
                dfs.append(df[['_time',metric_name]])
            else:
                dfs.append(df[metric_name])

            # dfs.append(df)
        print('len dfs: ',len(dfs))
        if len(dfs)>0:
            service_df = pd.concat(dfs,axis=1)
            out_dir = os.path.join(os.getcwd(),"data",now_time,str(i))
            if not os.path.exists(out_dir):
                print("making dir")
                os.makedirs(out_dir)
            # service_cols = ["_time"]+services[service]
            # service_df = pd.DataFrame(data_service,columns=service_cols)
            service_df.to_csv(os.path.join(out_dir,service+ ".csv"),index=False)
        
        

