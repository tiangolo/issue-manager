FROM python:3.7

RUN pip install PyGithub "pydantic==v1.0b2"

COPY ./app /app

CMD ["python", "/app/main.py"]
