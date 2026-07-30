# syntax=docker/dockerfile:1

FROM python:3.11-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY README.md LICENSE ./
COPY credit_risk/ ./credit_risk/
RUN uv sync --locked --no-dev

COPY scripts/ ./scripts/

ENV AWS_DEFAULT_REGION=eu-north-1

RUN --mount=type=secret,id=mlflow_tracking_uri \
    --mount=type=secret,id=mlflow_username \
    --mount=type=secret,id=mlflow_password \
    --mount=type=secret,id=aws_access_key_id \
    --mount=type=secret,id=aws_secret_access_key \
    MLFLOW_TRACKING_URI=$(cat /run/secrets/mlflow_tracking_uri) \
    MLFLOW_TRACKING_USERNAME=$(cat /run/secrets/mlflow_username) \
    MLFLOW_TRACKING_PASSWORD=$(cat /run/secrets/mlflow_password) \
    AWS_ACCESS_KEY_ID=$(cat /run/secrets/aws_access_key_id) \
    AWS_SECRET_ACCESS_KEY=$(cat /run/secrets/aws_secret_access_key) \
    uv run --no-sync scripts/fetch_model.py

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "--no-sync", "uvicorn", "credit_risk.api.main:app", "--host", "0.0.0.0", "--port", "8000"]