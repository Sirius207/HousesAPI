# HousesAPI
A RESTful API for 591 website

[![Build Status](https://travis-ci.com/Sirius207/HousesAPI.svg?branch=main)](https://travis-ci.com/github/Sirius207/HousesAPI)
[![Known Vulnerabilities](https://snyk.io/test/github/sirius207/HousesAPI/badge.svg)](https://snyk.io/test/github/sirius207/HousesAPI)
[![Maintainability](https://api.codeclimate.com/v1/badges/d68c05d10bcbc59f45aa/maintainability)](https://codeclimate.com/github/Sirius207/HousesAPI/maintainability)
[![codecov](https://codecov.io/gh/Sirius207/HousesAPI/branch/main/graph/badge.svg?token=91PJ2CWMR0)](https://codecov.io/gh/Sirius207/HousesAPI)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI?ref=badge_shield)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



[API Document](https://sirius207.github.io/HousesAPI/)

## Features

- [x] 591 Crawler
- [x] MongoDB Format
- [x] RESTful API with MongoDB
- [x] ElasticSearch Storage
- [x] Kibana Dashboard
- [ ] Aglio API Doc
- [ ] Crawler (Airflow Format)
- [ ] Prometheus Setup
- [ ] Grafana Dashboard

## Getting Started

### Prerequisites

* python ^3.7.3
* docker ^18.09.2
* docker-compose ^1.17.1
* Tesseract OCR

### Running Development

1. Install pipenv environment

```lan=shell
make init
pipenv shell
```

2. Activate MongoDB and ElasticSearch

a. add .env to environment/

b. setup [elasticSearch Account](https://www.elastic.co/guide/en/elastic-stack-get-started/7.13/get-started-docker.html#get-started-docker-tls) at first usage

```
cd environment
docker-compose -f create-certs.yml run --rm create_certs
docker-compose up -d
docker exec es01 /bin/bash -c "bin/elasticsearch-setup-passwords auto --batch --url https://es01:9200"
docker-compose down
```

c. setup ELASTICSEARCH_PASSWORD in .env

d. copy es01.crt & kib01.crt to your computer and set certificate
```
docker cp es01:/usr/share/elasticsearch/config/certificates/es01/es01.crt ./
docker cp es01:/usr/share/elasticsearch/config/certificates/kib01/kib01.crt  ./
```

e. restart
```
docker-compose up -d
```

f. setup filebeat
```
docker exec -it filebeat01 bash
filebeat modules enable mongodb
filebeat setup
filebeat -e
```

g. setup apm
```
docker exec -it apm01 bash
apm-server -e
```

### Running Production

Build API Docker Image
```
docker build . -t house-api-img --no-cache
docker run  --env-file .env --name house-api -d -p 5000:5000 house-api-img
```

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

create default api account
```
python api/loader/init_account.py
```

Execute Tests
```
make tests
```

create API Doc (Use [Aglio](https://github.com/danielgtaylor/aglio/issues))
```
aglio --theme-variables streak  -i api.apib --theme-template triple -o docs/api.html
```

#### Coding style tests

```lan=shell
make lint
```

#### Check MongoFB

```lan=shell
docker exec -it mongodb bash
mongo -u <user_name>
use <db>
```

### Changelog

* Check CHANGELOG.md

## Contributing

* Po-Chun, Lu

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI?ref=badge_large)