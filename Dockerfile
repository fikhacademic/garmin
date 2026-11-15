
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fitdecode \
    boto3 \
    psycopg[binary] \
    python-dotenv \
    dbt-postgres

CMD ["tail", "-f", "/dev/null"]
