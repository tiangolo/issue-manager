FROM python:3.10

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./app /code/app

ENV PYTHONPATH=/code/app

CMD ["python", "/code/app/main.py"]
