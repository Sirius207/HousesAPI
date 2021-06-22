# Changelog

## v0.1.4 (2021-06-22)

## Feat

- Enable MongoDB TLS Mode
- Let metricbeat connect to mongoDB with TLS
- Make API connect to MongoDB with TLS

## v0.1.3 (2021-06-14)

### Feat

- add schedule operation to crawler
- dockerize crawler
- connect csv_to_mongo to mongo via nginx proxy
- connect csv_to_es to elasticsearch with https via nginx proxy
- add api to docker-compose

### Update

- use bulk upsert instead of bulk insert in csv_to_mongo script


## v0.1.2 (2021-06-13)

### Feat

- Add argsparser to crawler

### Fix
- Prevent URLs crawler catch the same houses

### Doc

- Add requirements.txt for snyk checking

## v0.1.1 (2021-06-13)

### Feat

- Add api token authorization
- Add MongoDB Index
- Set ElasticSearch with TLS connection
- Add Kibana with TLS connection
- Add Filebeat, APM, Metricbeat support

### Update

- Add third method of phone number recognize
- Add ssl context in csv_to_es script

### Doc

- Add API Doc in docs dir

## v0.1.0 (2021-06-06)

- Housing Web Crawler
- REST API with MongoDB
- ElasticSearch and Kibana docker setup