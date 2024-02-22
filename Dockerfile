FROM python:3.11.3

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -U pip

RUN pip install -r /app/requirements.txt

COPY . /app

ENTRYPOINT ["python", "main.py"]
