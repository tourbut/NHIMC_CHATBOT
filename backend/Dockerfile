FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app/

LABEL maintainer="scshin88 <204415>"

RUN apt-get install tzdata
COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./backend/alembic.ini /app/alembic.ini
COPY ./backend/config/gunicorn_conf.py /app/gunicorn_conf.py
COPY ./backend/config/prestart.sh /app/prestart.sh
COPY ./backend/config/start.sh /app/start.sh