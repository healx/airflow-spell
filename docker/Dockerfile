FROM apache/airflow:2.2.4
USER root
COPY src/airflow_spell /opt/airflow/plugins
USER airflow
RUN /home/airflow/.local/bin/pip install "spell>=0.38.4,<1.0"
