docker_tag = airflow-spell

build:
	docker build --rm \
		--build-arg PYTHON_DEPS="spell==0.33.0" \
		-t $(docker_tag) \
		docker-airflow

webserver:
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		-v ${PWD}/airflow_spell:/development/airflow_spell \
		-e PYTHONPATH=/development \
		-p 8080:8080 \
		$(docker_tag) \
		webserver

list:
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		-v ${PWD}/airflow_spell:/development/airflow_spell \
		-e PYTHONPATH=/development \
		-ti \
		$(docker_tag) \
		airflow list_dags

run:
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		-v ${PWD}/airflow_spell:/development/airflow_spell \
		-e PYTHONPATH=/development \
		-ti \
		$(docker_tag) \
		bash


check: $(wildcard integration-test/dags/*.py)
	docker run --rm \
		-v ${PWD}/integration-test:/pwd/integration-test \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/integration-test/dags \
		-v ${PWD}/airflow_spell:/development/airflow_spell \
		-e PYTHONPATH=/development \
		$(docker_tag) \
		python /pwd/$<
