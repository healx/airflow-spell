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
