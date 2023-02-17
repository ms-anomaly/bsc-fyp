
from datetime import datetime, timedelta
import influxdb_client
import pandas as pd
import time
import os 
class query_generator:

    def __init__(self,client,bucket,measurement,container_names,fields,metric_names,services):
        self.bucket = bucket
        self.container_names = container_names
        self.fields = fields
        #self.range = range
        self.measurement = measurement
        self.client = client
        self.metric_names = metric_names
        self.services = services
        self.metric_ends = ["_sum","_count"]
    def generate_query(self,container_name,field,start=-10,end=0,flag_first=False,rt_metrics=False):
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
            |> keep(columns:["_time","_start","_stop","'+ field +'"])'
            
            return query
        elif not flag_first:
            query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: '+ str(start)+', stop: '+ str(end)+')\
            |> filter(fn:(r) => r._measurement == "'+self.measurement+'")\
            |> filter(fn:(r) => r.name == "'+container_name+'")\
            |> filter(fn:(r) => r._field == "'+field+'")\
            |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
            |> keep(columns:["'+ field +'"])'
            ##|> filter(fn:(r) => r._field == "'+ '" or r._field =="'.join(self.fields) +'")\ 
            print(start,end)
            return query
        # not used yet.
        elif rt_metrics:
            query = 'from(bucket:"'+self.bucket+'")\
            |> range(start: '+ str(start)+', stop: '+ str(end)+')\
            |> filter(fn:(r) => r._field == "'+field+'")'
            #|> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
            #|> keep(columns:["'+ field +'"])'
            ##|> filter(fn:(r) => r._field == "'+ '" or r._field =="'.join(self.fields) +'")\ 
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
            for d,container in enumerate(self.container_names):
                this_service = self.services[d]
                container_window_df = pd.DataFrame()
                for i,field in enumerate(self.fields):
                    query = ''
                    if (i == 0):
                        # set up time in dataframe
                        query = self.generate_query(container,field,start,end,flag_first=True,rt_metrics=False)
                    #end = range_st + window_size
                    else:
                        query = self.generate_query(container,field,start,end,flag_first=False,rt_metrics=False)
                    res = self.client.query_df(query)
                    # # #print(res.head())
                    # append res to data
                    container_window_df = pd.concat([container_window_df,res],axis=1)

               
                for x in self.metric_names:
                    service_name = x.split("_")[3]

                    if (service_name==this_service):
                        #for y in self.metric_ends:
                        #metric_name_comp = x + y
                        print(x)
                        query = 'from(bucket:"'+self.bucket+'")\
                                |> range(start: '+ str(start)+', stop: '+ str(end)+')\
                                |> filter(fn:(r) => r._field == "'+x+'")\
                                |> pivot(rowKey:["_time"], columnKey: ["_field"],valueColumn: "_value")\
                                |> keep(columns:["'+ x +'"])'
                        res = self.client.query_df(query)
                        print(res.size)
                        container_window_df = pd.concat([container_window_df,res],axis=1)

                        

                out_dir = os.path.join(os.getcwd(),"data",now_time,str(c))
                if not os.path.exists(out_dir):
                    print("making dir")
                    os.makedirs(out_dir)
                try:
                    container_window_df.to_csv(os.path.join(out_dir,container+ ".csv"))
                except:
                    print("ERROR IN CONVERTING TO STRING!")


class influx_data_client:
    def __init__(self,url,token,org):
        self.client = influxdb_client.InfluxDBClient(url,token,org,timeout=30_000)
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

#metrics = ["rt_cart_get_redis","rt_cart_delete_redis","rt_cart_post_redis","rt_cart_get_catalogue_categories","rt_cart_get_catalogue","rt_payment_post_rabbitmq","rt_shipping_get_count","rt_shipping_get_code","rt_shipping_get_calcid"
#,"rt_shipping_post_confirm","rt_user_get_redis","rt_user_get_mongo_checkid","rt_user_get_mongo_users","rt_user_post_login","rt_user_post_register","rt_user_post_order","rt_user_get_mongo_history","rt_dispatch_consume_rabbitmq"


metrics_new = ['rt_cart_delete_redis_bucket', 'rt_cart_get_catalogue_bucket', 'rt_cart_delete_redis_sum', 'rt_cart_delete_redis_count', 'rt_cart_get_catalogue_count', 'rt_cart_get_catalogue_sum', 'rt_cart_get_redis_bucket', 'rt_cart_get_redis_count', 'rt_cart_get_redis_sum', 'rt_cart_post_redis_bucket', 'rt_cart_post_redis_count', 'rt_cart_post_redis_sum', 'rt_dispatch_consume_rabbitmq_bucket', 'rt_dispatch_consume_rabbitmq_count', 'rt_dispatch_consume_rabbitmq_sum', 'rt_payment_post_rabbitmq_bucket', 'rt_payment_post_rabbitmq_count', 'rt_payment_post_rabbitmq_created', 'rt_payment_post_rabbitmq_sum', 'rt_user_get_mongo_checkid_bucket', 'rt_user_get_mongo_checkid_count', 'rt_user_get_mongo_checkid_sum', 'rt_user_get_mongo_history_bucket', 'rt_user_get_mongo_history_count', 'rt_user_get_mongo_history_sum', 'rt_user_get_redis_sum', 'rt_user_get_redis_count', 'rt_user_get_mongo_users_sum', 'rt_user_get_mongo_users_count', 'rt_user_get_mongo_users_bucket', 'rt_user_get_redis_bucket', 'rt_user_post_login_bucket', 'rt_user_post_login_count', 'rt_user_post_login_sum', 'rt_user_post_order_bucket', 'rt_user_post_order_count', 'rt_user_post_order_sum', 'rt_user_post_register_bucket', 'rt_user_post_register_count', 'rt_web_get_catalogue_allproduts_bucket', 'rt_web_get_catalogue_allproduts_count', 'rt_user_post_register_sum', 'rt_web_get_catalogue_categories_bucket', 'rt_web_get_catalogue_allproduts_sum', 'rt_web_get_catalogue_categories_sum', 'rt_web_get_catalogue_categories_count', 'rt_web_get_catalogue_productsfromcategories_bucket', 'rt_web_get_catalogue_productsfromcategories_count', 'rt_web_get_catalogue_productsfromcategories_sum', 'rt_web_get_catalogue_productsku_bucket', 'rt_web_get_catalogue_productsku_count', 'rt_web_get_catalogue_productsku_sum', 'rt_web_get_catalogue_search_bucket', 'rt_web_get_catalogue_search_count', 'rt_web_get_catalogue_search_sum','rt_shipping_get_citiescode_seconds_count','rt_shipping_get_citiescode_seconds_sum','rt_web_get_shipping_calcid_seconds_max','rt_web_get_shipping_calcid_seconds_count','rt_web_get_shipping_calcid_seconds_sum','rt_web_get_shipping_code_seconds_count','rt_web_get_shipping_code_seconds_max','rt_web_get_shipping_code_seconds_sum','rt_web_get_shipping_matchcode_seconds_count','rt_web_get_shipping_matchcode_seconds_max','rt_web_get_shipping_matchcode_seconds_sum','rt_web_get_shipping_postconfirm_seconds_count','rt_web_get_shipping_postconfirm_seconds_max','rt_web_get_shipping_postconfirm_seconds_sum']
metric_name_ends = ["_sum","_count"]
bucket = "robot-shop"
org = "fyp"

#token = "UEqwqE8noxgOpJetiDoEyf_OdVfwvLtcLLzVYNpG2V5Vl-Ratzi-1xOBa2aqoEDhkaHqVUvjqByWXwRj9i3pOw=="
token = "amcAeToLou5FOnvhv8czQYOfD_2fMIx2MjiUyZgpLBoRsXh0_HNQr1-i-hB92OsFeSH6nnhcoDeaVxiaCQLbSw=="
# Store the URL of your InfluxDB instance
url="http://10.8.100.247:8086"
#url="http://0.0.0.0:8086"
measurement_name = "prometheus_remote_write"
#containers = ["robot-shop_cart_1","robot-shop_catalogue_1"]
containers = ["robot-shop_web_1", "robot-shop_user_1" ,"robot-shop_shipping_1", "robot-shop_redis_1", "robot-shop_ratings_1", "robot-shop_rabbitmq_1", "robot-shop_payment_1", "robot-shop_mysql_1", "robot-shop_mongodb_1", "robot-shop_dispatch_1",  "robot-shop_cart_1", "robot-shop_catalogue_1"]
services = ["web", "users","shipping","redis","rating", "rabbitmq", "payment","mysql","mongo","dispatch","cart","catalogue"]
fields = ["container_memory_usage_bytes","container_cpu_usage_seconds_total","container_network_receive_bytes_total","container_network_receive_errors_total","container_network_transmit_bytes_total","container_network_transmit_errors_total"]
end_time = int(time.time())
st_time = 1676650000
client = influx_data_client(url,token,org)
query_gen = query_generator(client,bucket,measurement_name,containers,fields,metrics_new,services)
query_gen.get_csv(st_time,end_time)


#DB access _
#SeKy4l1Tddlw9H6CYG25eZx3k5-Wm6vUd1QK_C1KuRATiOW0mI_qLpiMmYWOo0qLwH7PLl8HB--wXO05PGDTOQ==


