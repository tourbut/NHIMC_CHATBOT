FROM pgvector/pgvector:pg16

# 로케일 생성에 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    locales \
    && rm -rf /var/lib/apt/lists/*

# ko_KR.UTF-8 로케일 생성
RUN localedef -i ko_KR -c -f UTF-8 -A /usr/share/locale/locale.alias ko_KR.UTF-8

# 로케일 설정
ENV LANG ko_KR.UTF-8
ENV LANGUAGE ko_KR:ko
ENV LC_ALL ko_KR.UTF-8