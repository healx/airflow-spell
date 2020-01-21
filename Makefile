build:
	docker build \
		--rm \
		--build-arg AIRFLOW_DEPS="slack" \
		--build-arg PYTHON_DEPS="boto3>=1.9" \
		-t puckel/docker-airflow docker-airflow

webserver:
	docker run \
		-v ${PWD}:/pwd \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/dags \
		-e AIRFLOW__CORE__PLUGINS_FOLDER=/pwd/plugins \
		-p 8080:8080 \
		puckel/docker-airflow \
		webserver


check: $(wildcard dags/*.py)
	docker run \
		-v ${PWD}:/pwd \
		-e AIRFLOW__CORE__DAGS_FOLDER=/pwd/dags \
		-e AIRFLOW__CORE__PLUGINS_FOLDER=/pwd/plugins \
		puckel/docker-airflow \
		python /pwd/$<
