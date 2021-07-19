FROM apache/airflow:2.1.2-python3.9
COPY . /opt/airflow-spell
USER root
RUN pip install /opt/airflow-spell
USER airflow
