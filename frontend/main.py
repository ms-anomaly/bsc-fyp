import http.client
import datetime
import time
import datetime
import requests
import json
import random



import const
import prom
import frontend

if __name__ == "__main__":
    while True:
        ######################################
        ##### Poll data from Prometheus ######
        ######################################

        data3D = prom.getData()

        # sampleDataNew = [[[1] * 22] * 12] * 24

        ######################################
        ####### Send request to Bento ########
        ######################################

        response = requests.post(
            prom.BENTOML + 'classify', 
            data=json.dumps(data3D),
            headers={"content-type":"application/json"}
        )

        results = response.json()
        # print(results)

        ######################################
        ####### Calculate SHAP Values ########
        ######################################


        ######################################
        ####### Output to front-end ########
        ######################################

        # node_colors = dict.fromkeys(const.services, 'lightgreen')
        # node_colors['payment'] = 'red'

        # frontend.drawServiceGraph(const.adj_matrix, const.services, node_colors, 'plots/serviceGraph.png')

        break


