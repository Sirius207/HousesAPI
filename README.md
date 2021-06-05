# HousesAPI
A RESTful API for 591 website


## Features

- [ ] 591 Crawler
- [ ] MongoDB Format
- [ ] RESTful API with MongoDB
- [ ] ElasticSearch Storage
- [ ] Kibana Dashboard
- [ ] Aglio API Doc
- [ ] Crawler (Airflow Format)
- [ ] Prometheus Setup
- [ ] Grafana Dashboard

## Getting Started

### Prerequisites

* python 3.7.3^
* docker 18.09.2^
* docker-compose 1.17.1^
* git

### Running Development

1. Install pipenv environment

```lan=shell
make init
pipenv shell
```

2. Activate MongoDB and ElasticSearch

a. add .env to environment/

b. Run docker containers

```
cd environment
docker-compose up -d
```

### Running Production

### Running the tests

#### Installing Dev Packages

```lan=shell
pipenv install --dev
```

#### Unit Test

Load Fake Data to MongoDB

```
cd services
export PYTHONPATH=$PYTHONPATH:$PWD
python api/loader/csv_to_mongo.py --file api/tests/api/fake_houses.csv
```

Execute Tests
```
make tests
```

#### Coding style tests

```lan=shell
make lint
```

### Changelog

* Check CHANGELOG.md

## Contributing

* Po-Chun, Lu