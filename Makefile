.PHONY: build up down list check
docker_tag = testing-airflow-spell

build:
	docker build --rm -t $(docker_tag) .

up:
	docker-compose up

down:
	docker-compose down

list:
	docker-compose exec webserver airflow list_dags

check: $(wildcard dags/*.py)
	docker-compose exec webserver python /usr/local/airflow/$<
