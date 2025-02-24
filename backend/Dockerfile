FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app/

LABEL maintainer="scshin88 <204415>"

RUN apt-get update && apt-get install -y \
    tzdata \
    locales \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 로케일 생성
RUN localedef -i ko_KR -c -f UTF-8 -A /usr/share/locale/locale.alias ko_KR.UTF-8
# 환경변수 설정
ENV LANG ko_KR.UTF-8
ENV LC_ALL ko_KR.UTF-8

COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./backend/alembic.ini /app/alembic.ini
COPY ./backend/config/gunicorn_conf.py /app/gunicorn_conf.py
COPY ./backend/config/prestart.sh /app/prestart.sh
COPY ./backend/config/start.sh /app/start.sh