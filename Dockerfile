FROM ubuntu:latest
LABEL authors="keplar01"
FROM python:3.10
WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
