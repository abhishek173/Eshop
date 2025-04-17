FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install django

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD python /app/manage.py runserver 0.0.0.0:8000