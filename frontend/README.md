# Frontend

This front end service will query data from the Prometheus service for
2 minute window and calls the ML model's API to get the prdictions.
Using the prediction it then calculates the SHAP values for each
feature and identify the anomalous service.

Build
```
docker build -t drac98/pipe .
```

Run
```
docker run -it --network robot-shop_robot-shop --rm -v /home/drac98/workspace/fyp/monitoring/frontend/plots:/app/plots drac98/pipe:latest
```