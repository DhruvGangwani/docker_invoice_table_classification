# syntax=docker/dockerfile:1

FROM python:3.6-slim-buster

WORKDIR .

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY . .

CMD ["python3.6", "app.py"]


