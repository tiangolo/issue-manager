FROM python:3.7

RUN pip install "PyGithub>=1.55,<2.0" "pydantic>=v1.8.2,<2.0"

COPY ./app /app

CMD ["python", "/app/main.py"]
