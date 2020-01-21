build:
	docker build . -t airflow-spell

webserver:
	docker run \
		--rm \
		-p 8080:8080 \
		airflow-spell \
		webserver

list:
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		-ti \
		airflow-spell \
		airflow list_dags

run:
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-ti \
		airflow-spell \
		bash


check: $(wildcard integration-test/dags/*.py)
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		airflow-spell \
		python /pwd/$<
