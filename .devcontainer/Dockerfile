FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /samaritan-pentateuch

RUN apt update && apt install -y --no-install-recommends \
    build-essential libpq-dev openssh-client git \
    && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/bin/bash" ]
