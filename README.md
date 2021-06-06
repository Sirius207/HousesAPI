# HousesAPI
A RESTful API for 591 website

[![Build Status](https://travis-ci.com/Sirius207/HousesAPI.svg?branch=main)](https://travis-ci.com/github/Sirius207/HousesAPI)
[![Known Vulnerabilities](https://snyk.io/test/github/sirius207/HousesAPI/badge.svg)](https://snyk.io/test/github/sirius207/HousesAPI)
[![Maintainability](https://api.codeclimate.com/v1/badges/d68c05d10bcbc59f45aa/maintainability)](https://codeclimate.com/github/Sirius207/HousesAPI/maintainability)
[![codecov](https://codecov.io/gh/Sirius207/HousesAPI/branch/main/graph/badge.svg?token=91PJ2CWMR0)](https://codecov.io/gh/Sirius207/HousesAPI)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FSirius207%2FHousesAPI?ref=badge_shield)


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

create default api account
```
python api/loader/init_account.py
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