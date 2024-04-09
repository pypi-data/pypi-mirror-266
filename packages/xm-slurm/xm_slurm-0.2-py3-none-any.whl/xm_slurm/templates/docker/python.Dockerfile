# syntax=docker/dockerfile:1.4
ARG BASE_IMAGE=docker.io/python:3.10-slim
FROM $BASE_IMAGE as builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install and update necesarry global Python packages
RUN pip install -U pip setuptools wheel pysocks

ARG PIP_REQUIREMENTS=requirements.txt

RUN python -m venv --copies --upgrade --upgrade-deps --system-site-packages /venv
COPY $PIP_REQUIREMENTS /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    PIP_CACHE_DIR=/root/.cache/pip /venv/bin/pip install -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt

COPY --link . /workspace
WORKDIR /workspace

ENTRYPOINT [ "/venv/bin/python" ]