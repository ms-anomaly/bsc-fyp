import const
import datetime
import requests

PROMETHEUS = 'http://prometheus:9090'
BENTOML = 'http://bento-fyp:3000/'
PROMETHEUS_ENDPOINT_INSTANT_QUERY = '/api/v1/query'
PROMETHEUS_ENDPOINT_RANGE_QUERY = '/api/v1/query_range'

def getData():
        lastVals = [0] * len(const.cumulative_cols)

        timeSteps = 24
        period = [ [[0] * 20] * 12 ] * 24

        ### Creating the 3D input: 24x12x20  (new model: 24x12x21) ###

        current_timestamp = datetime.datetime.now().timestamp()
        start_timestamp = datetime.datetime.fromtimestamp(current_timestamp-120).strftime("%Y-%m-%dT%H:%M:%S.%fZ") # endtime - 2 minutes
        end_timestamp = datetime.datetime.fromtimestamp(current_timestamp-5).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Iterate for 24 time steps (2 minutes)
        for step in range(1):

            # Iterate for each service
            for m, service in enumerate(const.containers):
                first = True

                # Iterate for each feature in a service
                for n, feature in enumerate(const.cumulative_cols):
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

                    # # DEBUG: Print service name
                    # if first:
                    #     print(dataV['result'][0]['metric']['name'])
                    #     first = False

                    # # DEBUG: Print each feature and its associated value
                    # if results['status']=="success":
                    #     print("-",dataV['result'][0]['metric']['__name__'], ':', dataV['result'][0]['value'])
                    #     print('\n\n\n')
                    # else:
                    #     print("Query failed: Poll {0} feature of service {1}".format(feature, service))

                    # period[step][m][n] = dataV['result'][0]['value'][0]

                    # # DEBUG: Print all 24 values of a feature
                    # print(m, n,": ", end="")
                    # for k, val in enumerate(dataV['result'][0]['values']):
                    #     print(val[0], end=" ")
                    #     period[k][m][n] = val[0]
                    # print("\n")


                    # oneServ.append(dataV['result'][0]['value'][0])


                for rt in const.other_cols:
                    pass

                for rt in const.rt_metrics:
                    pass
                
                # print('\n\n\n')
                # print('\n\n\n')
        
        return period

