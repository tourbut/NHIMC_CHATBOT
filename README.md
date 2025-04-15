# NHIMC_CHATBOT

국민건강보험 일산병원 챗봇 시스템

---

## 소개

NHIMC_CHATBOT은 국민건강보험 일산병원을 위한 AI 기반 챗봇 시스템입니다. FastAPI(Python) 백엔드와 SvelteKit(프론트엔드), PostgreSQL, Ollama 등 다양한 기술 스택을 활용하여, 사용자 맞춤형 챗봇, 텍스트 마이닝, 파일 기반 RAG, 관리자 기능 등을 제공합니다.

---

## 폴더 구조

```
NHIMC_CHATBOT/
│
├─ backend/                # 백엔드 FastAPI 서버
│   ├─ app/
│   │   ├─ main.py
│   │   ├─ models.py
│   │   ├─ alembic/        # DB 마이그레이션
│   │   ├─ core/           # 설정, 공통 모듈
│   │   ├─ src/
│   │   │   ├─ api.py
│   │   │   ├─ deps.py
│   │   │   ├─ crud/       # DB CRUD 로직
│   │   │   ├─ engine/     # LLM, 임베딩, 텍스트마이닝 등
│   │   │   ├─ routes/     # FastAPI 라우터
│   │   │   ├─ schemas/    # Pydantic/SQLModel 스키마
│   │   │   ├─ utils/      # 유틸리티 함수
│   ├─ config/             # Gunicorn, prestart 등 설정
│   ├─ files/              # 업로드 파일 저장
│   ├─ logs/               # 로그 파일
│   ├─ requirements.txt
│   ├─ Dockerfile
│   └─ ...
│
├─ frontend/               # 프론트엔드 SvelteKit
│   ├─ src/
│   │   ├─ lib/            # 공통 컴포넌트, API 모듈 등
│   │   ├─ routes/         # 페이지 라우트
│   │   ├─ app.css, app.html
│   ├─ static/             # 정적 파일(이미지 등)
│   ├─ package.json
│   ├─ tailwind.config.js
│   ├─ Dockerfile
│   └─ ...
│
├─ db/                     # DB 관련 파일 및 Dockerfile
├─ script/                 # 초기화 스크립트 등
├─ tester/                 # 테스트/실험용 코드
├─ docker-compose.yaml     # 전체 서비스 오케스트레이션
├─ README.md
└─ ...
```

---

## 주요 기능

### 사용자
- 회원가입 및 인증
- 채팅방 생성/관리 (CRUD)
- 사용자별 시스템 프롬프트 관리 및 공유
- 파일 업로드 및 파일 기반 RAG(문서 기반 질의응답)
- 텍스트마이닝(지시문, 스키마, 추출, 결과 관리)

### 관리자
- 전체 파일 업로드 및 관리
- 사용자/부서별 사용량 및 API키 관리
- 사용 제한 설정
- 회원 정보 및 채팅 내용 확인
- 시스템 프롬프트 및 LLM 관리

---

## 기술 스택

- **Backend**: Python, FastAPI, SQLModel, Alembic, LangChain, Ollama, PostgreSQL
- **Frontend**: SvelteKit, TailwindCSS, Flowbite, JavaScript
- **Infra**: Docker, Docker Compose, Nginx
- **ETC**: Markdown 변환, Embedding, RAG, 텍스트마이닝, LLM 연동

---

## 개발 및 실행

### 1. 개발 환경 준비

- Python 3.11+
- Node.js 18+
- Docker, Docker Compose

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
# DB 마이그레이션
alembic upgrade head
# 서버 실행
uvicorn app.main:app --reload
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

### 4. Docker Compose로 전체 실행

```bash
docker-compose up --build
```

---

## 기타

- DB 마이그레이션: `backend/app/alembic/versions/`
- 환경설정: `.env`, `backend/app/core/config.py`
- 커스텀 스크립트: `backend/app/config/prestart.sh`
- 자세한 환경 변수 및 Gunicorn 설정은 README 하단 참고

---

## Gunicorn 및 컨테이너 환경 변수 참고

(아래는 Gunicorn 및 컨테이너 환경 변수 설정 예시입니다. 상세 설명은 기존 README 하단 참고)

- `GUNICORN_CONF`: Gunicorn Python 설정 파일 경로
- `WORKERS_PER_CORE`: CPU 코어당 워커 수
- `MAX_WORKERS`: 최대 워커 수
- `WEB_CONCURRENCY`: 워커 프로세스 수 직접 지정
- `HOST`, `PORT`, `BIND`: 바인딩 주소 및 포트
- `LOG_LEVEL`: 로그 레벨
- `WORKER_CLASS`: 워커 클래스
- `TIMEOUT`, `KEEP_ALIVE`, `GRACEFUL_TIMEOUT`: 타임아웃 설정
- `ACCESS_LOG`, `ERROR_LOG`: 로그 파일 경로
- `GUNICORN_CMD_ARGS`: 추가 Gunicorn 커맨드라인 인자
- `PRE_START_PATH`: prestart.sh 스크립트 경로

---

## 참고

- [FastAPI 공식문서](https://fastapi.tiangolo.com/)
- [SvelteKit 공식문서](https://kit.svelte.dev/)
- [LangChain](https://python.langchain.com/)
- [Ollama](https://ollama.com/)

---

#### `GUNICORN_CONF`

The path to a Gunicorn Python configuration file.

By default:

* `/app/gunicorn_conf.py` if it exists
* `/app/app/gunicorn_conf.py` if it exists
* `/gunicorn_conf.py` (the included default)

You can set it like:

```bash
docker run -d -p 80:80 -e GUNICORN_CONF="/app/custom_gunicorn_conf.py" myimage
```

You can use the [config file from the base image](https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/gunicorn_conf.py) as a starting point for yours.

#### `WORKERS_PER_CORE`

This image will check how many CPU cores are available in the current server running your container.

It will set the number of workers to the number of CPU cores multiplied by this value.

By default:

* `1`

You can set it like:

```bash
docker run -d -p 80:80 -e WORKERS_PER_CORE="3" myimage
```

If you used the value `3` in a server with 2 CPU cores, it would run 6 worker processes.

You can use floating point values too.

So, for example, if you have a big server (let's say, with 8 CPU cores) running several applications, and you have a FastAPI application that you know won't need high performance. And you don't want to waste server resources. You could make it use `0.5` workers per CPU core. For example:

```bash
docker run -d -p 80:80 -e WORKERS_PER_CORE="0.5" myimage
```

In a server with 8 CPU cores, this would make it start only 4 worker processes.

**Note**: By default, if `WORKERS_PER_CORE` is `1` and the server has only 1 CPU core, instead of starting 1 single worker, it will start 2. This is to avoid bad performance and blocking applications (server application) on small machines (server machine/cloud/etc). This can be overridden using `WEB_CONCURRENCY`.

#### `MAX_WORKERS`

Set the maximum number of workers to use.

You can use it to let the image compute the number of workers automatically but making sure it's limited to a maximum.

This can be useful, for example, if each worker uses a database connection and your database has a maximum limit of open connections.

By default it's not set, meaning that it's unlimited.

You can set it like:

```bash
docker run -d -p 80:80 -e MAX_WORKERS="24" myimage
```

This would make the image start at most 24 workers, independent of how many CPU cores are available in the server.

#### `WEB_CONCURRENCY`

Override the automatic definition of number of workers.

By default:

* Set to the number of CPU cores in the current server multiplied by the environment variable `WORKERS_PER_CORE`. So, in a server with 2 cores, by default it will be set to `2`.

You can set it like:

```bash
docker run -d -p 80:80 -e WEB_CONCURRENCY="2" myimage
```

This would make the image start 2 worker processes, independent of how many CPU cores are available in the server.

#### `HOST`

The "host" used by Gunicorn, the IP where Gunicorn will listen for requests.

It is the host inside of the container.

So, for example, if you set this variable to `127.0.0.1`, it will only be available inside the container, not in the host running it.

It's is provided for completeness, but you probably shouldn't change it.

By default:

* `0.0.0.0`

#### `PORT`

The port the container should listen on.

If you are running your container in a restrictive environment that forces you to use some specific port (like `8080`) you can set it with this variable.

By default:

* `80`

You can set it like:

```bash
docker run -d -p 80:8080 -e PORT="8080" myimage
```

#### `BIND`

The actual host and port passed to Gunicorn.

By default, set based on the variables `HOST` and `PORT`.

So, if you didn't change anything, it will be set by default to:

* `0.0.0.0:80`

You can set it like:

```bash
docker run -d -p 80:8080 -e BIND="0.0.0.0:8080" myimage
```

#### `LOG_LEVEL`

The log level for Gunicorn.

One of:

* `debug`
* `info`
* `warning`
* `error`
* `critical`

By default, set to `info`.

If you need to squeeze more performance sacrificing logging, set it to `warning`, for example:

You can set it like:

```bash
docker run -d -p 80:8080 -e LOG_LEVEL="warning" myimage
```

#### `WORKER_CLASS`

The class to be used by Gunicorn for the workers.

By default, set to `uvicorn.workers.UvicornWorker`.

The fact that it uses Uvicorn is what allows using ASGI frameworks like FastAPI, and that is also what provides the maximum performance.

You probably shouldn't change it.

But if for some reason you need to use the alternative Uvicorn worker: `uvicorn.workers.UvicornH11Worker` you can set it with this environment variable.

You can set it like:

```bash
docker run -d -p 80:8080 -e WORKER_CLASS="uvicorn.workers.UvicornH11Worker" myimage
```

#### `TIMEOUT`

Workers silent for more than this many seconds are killed and restarted.

Read more about it in the [Gunicorn docs: timeout](https://docs.gunicorn.org/en/stable/settings.html#timeout).

By default, set to `120`.

Notice that Uvicorn and ASGI frameworks like FastAPI are async, not sync. So it's probably safe to have higher timeouts than for sync workers.

You can set it like:

```bash
docker run -d -p 80:8080 -e TIMEOUT="20" myimage
```

#### `KEEP_ALIVE`

The number of seconds to wait for requests on a Keep-Alive connection.

Read more about it in the [Gunicorn docs: keepalive](https://docs.gunicorn.org/en/stable/settings.html#keepalive).

By default, set to `2`.

You can set it like:

```bash
docker run -d -p 80:8080 -e KEEP_ALIVE="20" myimage
```

#### `GRACEFUL_TIMEOUT`

Timeout for graceful workers restart.

Read more about it in the [Gunicorn docs: graceful-timeout](https://docs.gunicorn.org/en/stable/settings.html#graceful-timeout).

By default, set to `120`.

You can set it like:

```bash
docker run -d -p 80:8080 -e GRACEFUL_TIMEOUT="20" myimage
```

#### `ACCESS_LOG`

The access log file to write to.

By default `"-"`, which means stdout (print in the Docker logs).

If you want to disable `ACCESS_LOG`, set it to an empty value.

For example, you could disable it with:

```bash
docker run -d -p 80:8080 -e ACCESS_LOG= myimage
```

#### `ERROR_LOG`

The error log file to write to.

By default `"-"`, which means stderr (print in the Docker logs).

If you want to disable `ERROR_LOG`, set it to an empty value.

For example, you could disable it with:

```bash
docker run -d -p 80:8080 -e ERROR_LOG= myimage
```

#### `GUNICORN_CMD_ARGS`

Any additional command line settings for Gunicorn can be passed in the `GUNICORN_CMD_ARGS` environment variable.

Read more about it in the [Gunicorn docs: Settings](https://docs.gunicorn.org/en/stable/settings.html#settings).

These settings will have precedence over the other environment variables and any Gunicorn config file.

For example, if you have a custom TLS/SSL certificate that you want to use, you could copy them to the Docker image or mount them in the container, and set [`--keyfile` and `--certfile`](http://docs.gunicorn.org/en/latest/settings.html#ssl) to the location of the files, for example:

```bash
docker run -d -p 80:8080 -e GUNICORN_CMD_ARGS="--keyfile=/secrets/key.pem --certfile=/secrets/cert.pem" -e PORT=443 myimage
```

**Note**: instead of handling TLS/SSL yourself and configuring it in the container, it's recommended to use a "TLS Termination Proxy" like [Traefik](https://docs.traefik.io/). You can read more about it in the [FastAPI documentation about HTTPS](https://fastapi.tiangolo.com/deployment/#https).

#### `PRE_START_PATH`

The path where to find the pre-start script.

By default, set to `/app/prestart.sh`.

You can set it like:

```bash
docker run -d -p 80:8080 -e PRE_START_PATH="/custom/script.sh" myimage
```

### Custom Gunicorn configuration file

The image includes a default Gunicorn Python config file at `/gunicorn_conf.py`.

It uses the environment variables declared above to set all the configurations.

You can override it by including a file in:

* `/app/gunicorn_conf.py`
* `/app/app/gunicorn_conf.py`
* `/gunicorn_conf.py`

### Custom `/app/prestart.sh`

If you need to run anything before starting the app, you can add a file `prestart.sh` to the directory `/app`. The image will automatically detect and run it before starting everything.

For example, if you want to add Alembic SQL migrations (with SQLALchemy), you could create a `./app/prestart.sh` file in your code directory (that will be copied by your `Dockerfile`) with:

```bash
#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
```

and it would wait 10 seconds to give the database some time to start and then run that `alembic` command.

If you need to run a Python script before starting the app, you could make the `/app/prestart.sh` file run your Python script, with something like:

```bash
#! /usr/bin/env bash

# Run custom Python script before starting
python /app/my_custom_prestart_script.py
```

You can customize the location of the prestart script with the environment variable `PRE_START_PATH` described above.

### Development live reload

The default program that is run is at `/start.sh`. It does everything described above.

There's also a version for development with live auto-reload at:

```bash
/start-reload.sh
```

#### Details

For development, it's useful to be able to mount the contents of the application code inside of the container as a Docker "host volume", to be able to change the code and test it live, without having to build the image every time.

In that case, it's also useful to run the server with live auto-reload, so that it re-starts automatically at every code change.

The additional script `/start-reload.sh` runs Uvicorn alone (without Gunicorn) and in a single process.

It is ideal for development.

#### Usage

For example, instead of running:

```bash
docker run -d -p 80:80 myimage
```

You could run:

```bash
docker run -d -p 80:80 -v $(pwd):/app myimage /start-reload.sh
```

* `-v $(pwd):/app`: means that the directory `$(pwd)` should be mounted as a volume inside of the container at `/app`.
    * `$(pwd)`: runs `pwd` ("print working directory") and puts it as part of the string.
* `/start-reload.sh`: adding something (like `/start-reload.sh`) at the end of the command, replaces the default "command" with this one. In this case, it replaces the default (`/start.sh`) with the development alternative `/start-reload.sh`.