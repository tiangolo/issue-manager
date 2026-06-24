FROM ghcr.io/astral-sh/uv:0.9.11-python3.14-trixie-slim

ENV UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /code

COPY ./pyproject.toml ./uv.lock /code/

RUN uv sync --locked

COPY ./app /code/app

ENV PYTHONPATH=/code/app

CMD ["uv", "run", "python", "/code/app/main.py"]
