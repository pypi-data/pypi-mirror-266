# syntax=docker/dockerfile:1.4
ARG BASE_IMAGE

FROM $BASE_IMAGE AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip setuptools wheel pysocks \
    && pip install pdm

COPY --link pyproject.toml pdm.lock /workspace/
WORKDIR /workspace

RUN --mount=type=cache,target=/root/.cache/pdm mkdir __pypackages__ \
    && PDM_CACHE_DIR=/root/.cache/pdm pdm sync --prod --no-editable

FROM $BASE_IMAGE

ARG PYTHON_MAJOR
ARG PYTHON_MINOR

ENV PYTHONPATH=/workspace/pkgs:$PYTHONPATH
COPY --link --from=builder /workspace/__pypackages__/$PYTHON_MAJOR.$PYTHON_MINOR/lib /workspace/pkgs

WORKDIR /workspace/src
COPY --link . /workspace/src

ENTRYPOINT ["python"]