FROM python:3.14.6-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

ENV UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /code

COPY ./pyproject.toml ./uv.lock /code/

RUN uv sync --locked

COPY ./app /code/app

ENV PYTHONPATH=/code/app

CMD ["uv", "run", "python", "/code/app/main.py"]
