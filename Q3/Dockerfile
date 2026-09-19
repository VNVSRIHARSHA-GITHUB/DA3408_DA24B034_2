
FROM python:3.10-slim

WORKDIR /app

COPY shard_validator.py .
COPY shards/ /shards/

ENV SHARD_DIR=/shards

ENTRYPOINT ["python", "shard_validator.py"]