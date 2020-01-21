build:
	docker build . -t airflow-spell

webserver:
	docker run \
		--rm \
		-p 8080:8080 \
		airflow-spell \
		webserver

list:
	docker run \
		--rm \
		-ti \
		airflow-spell \
		airflow list_dags

run:
	docker run \
		--rm \
		-ti \
		airflow-spell \
		bash


check: $(wildcard dags/*.py)
	docker run \
		-v ${PWD}:/pwd \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/dags \
		-e AIRFLOW__CORE__PLUGINS_FOLDER=/pwd/plugins \
		airflow-spell \
		python /pwd/$<
