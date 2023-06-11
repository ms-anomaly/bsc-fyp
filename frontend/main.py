import http.client
import datetime
import time
import datetime
import requests
import json
import random

import torch
import torch.nn as nn
import numpy as np

import const
import prom
import frontend
import localization
from localization import *

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
        print(results)

        ######################################
        ####### Calculate SHAP Values ########
        ######################################

        anomalyNo = 0
        for i in results:
            if i[0]>=3.51:
                anomalyNo += 1
        
        if anomalyNo>3:
            sig = nn.Sigmoid()
            # model = "model/explainer.pkl"
            localizer = localization.Localize(sig)
            
            suspect_services, suspect_features = localizer.localize_anomaly(torch.tensor(data3D).to(torch.float32) , torch.tensor(results).to(torch.float32))

        print(const.services[suspect_services[-1]])
        print(const.cols_with_rt[suspect_features[-1]])

        ######################################
        ####### Output to front-end ########
        ######################################

        node_colors = dict.fromkeys(const.services, 'lightgreen')
        node_colors[const.services[suspect_services[-1]]] = 'red'

        print(node_colors)

        frontend.drawServiceGraph(const.adj_matrix, const.services, node_colors, 'plots/serviceGraph.png')

        break
