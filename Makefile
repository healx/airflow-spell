.PHONY: build up down list check
docker_tag = testing-airflow-spell
docker_dir = docker


# import settings config
settingsfile=${PWD}/settings.env
ifneq ("$(wildcard $(settingsfile))","")
	ifdef stt
	settingsfile=$(stt)
	endif
	include $(settingsfile)
	export $(shell sed 's/=.*//' $(settingsfile))
endif


build:
	docker build --rm \
		-t $(docker_tag) \
		-f $(docker_dir)/Dockerfile \
		.

up:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		up

down:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		down

run:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver bash

add-spell-connection:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver airflow connections -a \
		--conn_type http \
		--conn_id spell_conn_id \
		--conn_password ${SPELL_TOKEN}

list:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver airflow list_dags

check: $(wildcard dags/*.py)
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver python /usr/local/airflow/$<

release:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine check dist/*

upload-release: release
	twine upload dist/*

upload-private-release: export TWINE_USERNAME=aws
upload-private-release: export TWINE_PASSSWORD=$(shell aws codeartifact get-authorization-token --domain harper --domain-owner $(AWS_ACCOUNT_ID) --query authorizationToken --output text)
upload-private-release: export TWINE_REPOSITORY_URL=$(shell aws codeartifact get-repository-endpoint --domain harper --domain-owner $(AWS_ACCOUNT_ID) --repository v0 --format pypi --query repositoryEndpoint --output text)
upload-private-release: release
ifndef AWS_ACCOUNT_ID
	$(error AWS_ACCOUNT_ID is undefined)
endif
	TWINE_NON_INTERACTIVE=true twine upload --verbose --repository-url $$TWINE_REPOSITORY_URL dist/*
