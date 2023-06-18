import const
import datetime
import requests
import pandas as pd
import torch

PROMETHEUS = 'http://prometheus:9090'
BENTOML = 'http://bento-fyp:3000/'
PROMETHEUS_ENDPOINT_INSTANT_QUERY = '/api/v1/query'
PROMETHEUS_ENDPOINT_RANGE_QUERY = '/api/v1/query_range'

def getData():
        lastVals = [0] * len(const.cumulative_cols)

        timeSteps = 24
        period = [ [[0] * 22] * 12 ] * 24

        ### Creating the 3D input: 24x12x20  (new model: 24x12x21) ###

        current_timestamp = datetime.datetime.now().timestamp()
        start_timestamp = datetime.datetime.fromtimestamp(current_timestamp-1800-120).strftime("%Y-%m-%dT%H:%M:%S.%fZ") # endtime - 2 minutes
        end_timestamp = datetime.datetime.fromtimestamp(current_timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        window_30min_timestamp = datetime.datetime.fromtimestamp(current_timestamp-1800).strftime("%Y-%m-%dT%H:%M:%S.%fZ") # endtime - 2 minutes

        print(start_timestamp, end_timestamp)
        # Iterate for each service
        dfs = dict()
        for m, service in enumerate(const.containers):
            first = True
            arr = []
            # Iterate for each feature in a service
            n = 0
            for _, feature in enumerate(const.cumulative_cols + const.other_cols):
                q = '{0}{{name="{1}"}}'.format(feature, service)
                # response = requests.get(PROMETHEUS + PROMETHEUS_ENDPOINT_INSTANT_QUERY, params={'query': q, 'time': datetime.datetime.fromtimestamp(current_timestamp-5*step).strftime("%Y-%m-%dT%H:%M:%S.%fZ")})

                # Start and end times are inclusive in range query
                response = requests.get(PROMETHEUS + PROMETHEUS_ENDPOINT_RANGE_QUERY, 
                                        params={
                                            'query': q,
                                            'start': start_timestamp,
                                            'end': end_timestamp,
                                            'step':'5s'
                                            })
                # print(q, start_timestamp, end_timestamp)

                results = response.json()
                # DEBUG
                # print(results)
                dataV = results['data']

                # DEBUG: Print all 19 values of a feature
                # print(m, n,": ", end="")
                if len(dataV['result']) < 1:
                    break
                periodData = dataV['result'][0]['values']
                try:
                    df = pd.DataFrame(periodData,columns=[feature])
                    df = df.fillna(method='ffill')
                    if feature in const.cumulative_cols:
                        df[col] = df[col].diff()
                        df[col].loc[df[col] < 0] = 0
                    # print(periodData)
                except Exception as e:
                    print("Error: ",e)
                    df = pd.DataFrame(0.000001, index=range(384), columns=[feature])
                arr.append(df)
            arr_rt = []
            for i,rt_feature in enumerate(const.rt_per_service[service]):
                q = '{0}'.format(rt_feature)

                # Start and end times are inclusive in range query
                response = requests.get(PROMETHEUS + PROMETHEUS_ENDPOINT_RANGE_QUERY, 
                                        params={
                                            'query': q,
                                            'start': start_timestamp,
                                            'end': end_timestamp,
                                            'step':'5s'
                                            })

                results = response.json()
                # DEBUG
                # print(results)
                dataV = results['data']
                
                # print(dataV['result'][0]['values'])
                periodData = dataV['result'][0]['values']
                data30min = [float(i[1]) for i in periodData]
                try:
                    df = pd.DataFrame(data30min,columns=[rt_feature])
                    # df = df.interpolate(method ='linear', limit_direction ='both')
                    df = df.fillna(method='ffill')
                    df = df.fillna(method='bfill')
                    for col in df.columns:
                        if col.split('_')[-1] == 'sum':
                            df[col] = df[col].diff()
                            df[col].loc[df[col] < 0] = 0
                except Exception as e:
                    print("Error: ",e)
                    df = pd.DataFrame(5000, index=range(384), columns=[rt_feature])
                arr_rt.append(df)
            
            df = pd.concat(arr,axis=1)
            df_rt = pd.concat(arr_rt,axis=1)
            df['sum'] = df_rt.sum(axis=1)/len(df_rt.columns)
            dfs[service] = df

        for service in const.containers:
            
            try:
                ma = df['sum'].rolling(window=24,min_periods=1).mean()
                q = pd.DataFrame(sum)
                df['ma']= df['sum'] - ma

                ma20 = df['sum'].rolling(window=24*10,min_periods=1).mean()
                df['ma20']= df['sum'] - ma20
            except Exception as e:
                print("Error: ",e)
                df['sum'] = pd.Series([0] * 384)            
                df['ma'] = pd.Series([0] * 384)           
                df['ma20'] = pd.Series([0] * 384)  

        period = torch.tensor(q.values.tolist())[-24:]       
            
                
                        
                
            
            

        return period

if __name__=="__main__":
    a = getData()
    print(len(a))