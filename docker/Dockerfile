FROM apache/airflow:1.10.10

USER root
RUN sudo apt update && sudo apt install gcc python3-dev -y && sudo apt clean

RUN pip install --upgrade pip
RUN pip install spell
COPY . /opt/airflow-spell
RUN pip install --no-deps /opt/airflow-spell
USER airflow
