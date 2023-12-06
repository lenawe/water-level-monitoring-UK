FROM python:3.10.0

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
  
WORKDIR /app

COPY data_app.py data_app.py
COPY .streamlit/ .streamlit/

ENTRYPOINT ["streamlit", "run", "data_app.py", "--server.port=8501", "--server.address=0.0.0.0"]