FROM python:3.11

LABEL maintainer="Raaid-Khan"


WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt  

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt &&\
    rm -rf /tmp 


COPY . /code/

COPY ./scripts /scripts


ENV PATH="/scripts:/py/bin:$PATH"

EXPOSE 8000 8501

CMD ["run", "uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["run.sh"]
