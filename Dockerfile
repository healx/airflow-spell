FROM puckel/docker-airflow:latest

# install the airflow-spell package
USER root
RUN mkdir /build-airflow-spell
COPY airflow_spell /build-airflow-spell/airflow_spell
COPY setup.py /build-airflow-spell/
RUN python -m pip install -e /build-airflow-spell
USER airflow

CMD ["webserver"]
