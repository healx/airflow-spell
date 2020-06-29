FROM apache/airflow:1.10.10
COPY . /opt/airflow-spell
USER root
RUN pip install /opt/airflow-spell
USER airflow
