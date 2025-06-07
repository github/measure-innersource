#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13-slim@sha256:d97b595c5f4ac718102e5a5a91adaf04b22e852961a698411637c718d45867c8
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
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u2 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/measure_innersource.py"]
ENTRYPOINT ["python3", "-u"]
