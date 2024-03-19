FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt \
    && rm requirements.txt

COPY ./app /app
WORKDIR /app

EXPOSE 5000

CMD ["python", "app.py"]
