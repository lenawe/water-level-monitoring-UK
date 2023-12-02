FROM apache/airflow:2.7.3

COPY requirements.txt .

COPY ./config/airflow.cfg /opt/airflow/airflow.cfg

RUN pip install --no-cache-dir --upgrade -r requirements.txt