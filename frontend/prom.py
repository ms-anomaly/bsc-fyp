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
                    df = pd.DataFrame(periodData,columns=['time',feature])
                    df[feature] = df[feature].astype(float).fillna(method='ffill')
                    df[feature] = df[feature].fillna(method='ffill')
                    if feature in const.cumulative_cols:
                        df[feature] = df[feature].diff()
                        df[feature].loc[df[feature] < 0] = 0
                    # print(periodData)
                except Exception as e:
                    print("Error1: ",e)
                    df = pd.DataFrame(0.000001, index=range(384), columns=[feature])
                arr.append(df[feature])
            arr_rt = []
            for i,rt_feature in enumerate(const.rt_per_service[service.split('-')[-2]]):
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
                    df[rt_feature] = df[rt_feature].astype(float).fillna(method='ffill')
                    df[rt_feature] = df[rt_feature].fillna(method='bfill')
                    for col in df.columns:
                        if col.split('_')[-1] == 'sum':
                            df[col] = df[col].diff()
                            df[col].loc[df[col] < 0] = 0
                except Exception as e:
                    print("Error2: ",e)
                    df = pd.DataFrame(5000, index=range(384), columns=[rt_feature])
                arr_rt.append(df[rt_feature])
            
            df = pd.concat(arr,axis=1)
            try:
                df_rt = pd.concat(arr_rt,axis=1)
                df['sum'] = df_rt.sum(axis=1)/len(df_rt.columns)
                dfs[service] = df
            except:
                df_rt = pd.DataFrame(5000, index=range(384))
                df['sum'] = df_rt.sum(axis=1)/len(df_rt.columns)
                dfs[service] = df
                print("rt sum error")

        for service in const.services:
            
            try:
                ma = dfs[service]['sum'].rolling(window=24,min_periods=1).mean()
                
                dfs[service]['ma']= dfs[service]['sum'] - ma

                ma20 = dfs[service]['sum'].rolling(window=24*10,min_periods=1).mean()
                dfs[service]['ma20']= dfs[service]['sum'] - ma20
            except Exception as e:
                print("Error3: ",e)
                dfs[service]['sum'] = pd.DataFrame(0.001, index=range(384), columns=[rt_feature])           
                dfs[service]['ma'] = pd.DataFrame(0.001, index=range(384), columns=[rt_feature])           
                dfs[service]['ma20'] = pd.DataFrame(0.001, index=range(384), columns=[rt_feature]) 
        t = []
        for i in dfs.keys():
            
            t.append(torch.tensor(dfs[i].values.tolist())[-24:])
        period = torch.stack(t)
            
                
                        
                
            
            

        return period

if __name__=="__main__":
    a = getData()
    print(len(a))