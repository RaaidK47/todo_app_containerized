FROM python:3.11

LABEL maintainer="Raaid-Khan"


WORKDIR /code

COPY ./requirements.txt /tmp/requirements.txt  

COPY . /code/

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    /py/bin/pip install -r /tmp/requirements.txt

COPY ./requirements2.txt /tmp/requirements2.txt  

RUN pip install -r /tmp/requirements2.txt &&\
    rm -rf /tmp 

EXPOSE 8000

CMD ["run", "uvicorn", "todo_app.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]