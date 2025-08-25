#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13.7-slim@sha256:8220ccec22e88cddd9a541cacd1bf48423bda8cdeb1015249e4b298edf86cdc7
LABEL com.github.actions.name="measure-innersource" \
    com.github.actions.description="Measure and report on the InnerSource collaboration occuring in a given repository" \
    com.github.actions.icon="bar-chart" \
    com.github.actions.color="white" \
    maintainer="@zkoppert" \
    org.opencontainers.image.url="https://github.com/github/measure-innersource" \
    org.opencontainers.image.source="https://github.com/github/measure-innersource" \
    org.opencontainers.image.documentation="https://github.com/github/measure-innersource" \
    org.opencontainers.image.vendor="GitHub" \
    org.opencontainers.image.description="Measure and report on the InnerSource collaboration occuring in a given repository"

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.47.2-0.2 \
    && rm -rf /var/lib/apt/lists/*

# HEALTHCHECK: 
# - Verifies the main script still exists (guards against accidental volume overlays)
# - Verifies Python can start
# Exit 0 = healthy, non‑zero = unhealthy
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python3 -c "import os, sys; sys.exit(0 if os.path.isfile('/action/workspace/measure_innersource.py') else 1)"

CMD ["/action/workspace/measure_innersource.py"]
ENTRYPOINT ["python3", "-u"]
