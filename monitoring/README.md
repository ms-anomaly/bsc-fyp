![monitoring-service-arch](fyp-monitoring.jpg)

To run the services
```
docker-compose up
```

Change the following environmental variable according to your setup<br>
`DOCKER_INFLUXDB_INIT_USERNAME`<br>
`DOCKER_INFLUXDB_INIT_PASSWORD`<br>
`DOCKER_INFLUXDB_INIT_ORG`<br>
`DOCKER_INFLUXDB_INIT_BUCKET`<br>
`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`

These variables are in the following files
1. docker-compose.yml
2. telegraf/mytelegraf.conf
3. telegraf/influxv2.env
