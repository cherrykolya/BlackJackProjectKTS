FROM python:3.9

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

ENV POSTGRES_USER = "postgres"
ENV POSTGRES_PASSWORD = "postgres"
ENV POSTGRES_DB = "blackjack1"

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

EXPOSE 5432

ENV TZ Europe/Moscow

CMD ["python", "main.py"]