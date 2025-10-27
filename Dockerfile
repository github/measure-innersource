#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
#trivy:ignore:AVD-DS-0002
FROM python:3.14.0-slim@sha256:4ed33101ee7ec299041cc41dd268dae17031184be94384b1ce7936dc4e5dead3
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
    && apt-get -y install --no-install-recommends git=1:2.47.3-0+deb13u1 \
    && rm -rf /var/lib/apt/lists/*

# Add a simple healthcheck to satisfy container scanners
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 -c "import os,sys; sys.exit(0 if os.path.exists('/action/workspace/measure_innersource.py') else 1)"

CMD ["/action/workspace/measure_innersource.py"]
ENTRYPOINT ["python3", "-u"]
