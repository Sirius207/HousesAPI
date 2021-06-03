PKG = services

.PHONY: init flake8 pylint lint test clean

init: clean
	pipenv --python 3.9
	pipenv install --dev
	pipenv run pre-commit install

ci-bundle: lint test

lint: pylint flake8

flake8:
	pipenv run flake8 $(PKG)/ --max-line-length=120

pylint:
	pipenv run pylint $(PKG)

mypy:
	pipenv run mypy $(PKG) --config-file setup.cfg

build: clean build-cython clean-modules

build-cython:
	cp Pipfile Pipfile.lock cython/
	cp -r $(PKG) cython/
	docker build -t $(PKG) cython/ --no-cache

clean-modules:
	rm -f cython/Pipfile*
	rm -rf cython/$(PKG)

test:
	pipenv run pytest -vv
