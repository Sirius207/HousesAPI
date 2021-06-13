# HousesAPI
A RESTful API for 591 website

[![Build Status](https://travis-ci.com/Sirius207/HousesAPI.svg?branch=main)](https://travis-ci.com/github/Sirius207/HousesAPI)
[![Known Vulnerabilities](https://snyk.io/test/github/sirius207/HousesAPI/badge.svg)](https://snyk.io/test/github/sirius207/HousesAPI)
[![Maintainability](https://api.codeclimate.com/v1/badges/d68c05d10bcbc59f45aa/maintainability)](https://codeclimate.com/github/Sirius207/HousesAPI/maintainability)
[![codecov](https://codecov.io/gh/Sirius207/HousesAPI/branch/main/graph/badge.svg?token=91PJ2CWMR0)](https://codecov.io/gh/Sirius207/HousesAPI)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI?ref=badge_shield)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Features

- [x] 591 house data Crawler
- [x] RESTful API with MongoDB for house data querying and creating
- [x] RESTful API with Token Authorization
- [x] API Doc built with Aglio
- [x] ElasticSearch Storage
- [x] House Data with Kibana Display
- [x] Filebeat Log Dashboard for MongoDB
- [x] APM Dashboard for API application
- [x] Metricbeat Dashboard for MongoDB

## Documents

- [API Document](https://sirius207.github.io/HousesAPI/)

## Getting Started

### Prerequisites

* python ^3.7.3
* docker ^18.09.2
* docker-compose ^1.17.1
* Tesseract OCR ^4.x


### Running Development

a. Install pipenv environment

```lan=shell
make init
pipenv shell
```

b. Activate MongoDB
```
cd docker-manifests
docker-compose -f docker-mongo.yml up -d
```

c. Activate ElasticSearch, Kibana

1. add .env to environment/

2. setup [elasticSearch Account](https://www.elastic.co/guide/en/elastic-stack-get-started/7.13/get-started-docker.html#get-started-docker-tls) at first usage

```
cd docker-manifests
docker-compose -f create-certs.yml run --rm create_certs
docker-compose -f docker-elastic.yml up -d
docker exec es01 /bin/bash -c "bin/elasticsearch-setup-passwords auto --batch --url https://es01:9200"
docker-compose -f docker-elastic.yml down
```

3. setup ELASTICSEARCH_PASSWORD in .env

4. copy es01.crt & kib01.crt to your computer and set certificate
```
docker cp es01:/usr/share/elasticsearch/config/certificates/es01/es01.crt ./
docker cp es01:/usr/share/elasticsearch/config/certificates/kib01/kib01.crt  ./
```

5. restart elasticsearch & kibana
```
docker-compose  -f docker-elastic.yml up -d
```

d. Activate Filebeat, APM, MetricBeat

1. start filebeat, apm, metricbeat
```
cd docker-manifests
docker-compose -f docker-beats.yml up -d
```

2. setup filebeat
```
docker exec -it filebeat01 bash
filebeat setup
filebeat -e
```

3. setup apm
```
docker exec -it apm01 bash
apm-server -e
```

4. setup metricbeat
```
docker exec -it metricbeat01 bash
metricbeat01 setup
metricbeat01 -e
```

e. Execute Crawler

parse house data in Taipei (city_id=1) and Export House data to csv
```
cd services
export PYTHONPATH=$PYTHONPATH:$PWD

python crawler/main.py \
    --urls_file data/urls.csv \
    --data_file data/temp_info.csv\
    --city_id 1 \
    --url_start 0 \
    --url_end 250
```
f. Import Data to Database

1. Import house data to MongoDB (from csv)

```
py api/loader/csv_to_mongo.py --file data/temp_info.csv
```

2. Import house data to Elasticsearch (from csv)


```
py api/loader/csv_to_es.py --file data/temp_info.csv
```

g. Start RESTful API
```
python api/app.py
```

### Running Production (API)

Build API Docker Image
```
docker build . -t house-api-img --no-cache
```

Start WSGI in Container
```
docker run  --env-file .env --name house-api -d -p 5000:5000 house-api-img
```

### Running the tests

#### Installing Dev Packages

```lan=shell
pipenv install --dev
```

#### Unit Test

Insert Fake Data to MongoDB

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

#### Check MongoDB Data

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