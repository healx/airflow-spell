.PHONY: build up down list check
docker_tag = testing-airflow-spell
docker_dir = docker

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

list:
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver airflow list_dags

check: $(wildcard dags/*.py)
	docker-compose \
		-f $(docker_dir)/docker-compose.yml \
		exec webserver python /usr/local/airflow/$<
