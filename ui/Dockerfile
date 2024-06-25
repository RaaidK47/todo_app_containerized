FROM python:3.11

LABEL maintainer="Raaid-Khan"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt  

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt &&\
    rm -rf /tmp 

# Add new libraries to requirements2.txt > Only these will be re-installed instead of all libraries   
COPY ./requirements2.txt /tmp/requirements2.txt  


RUN pip install -r /tmp/requirements2.txt &&\
    rm -rf /tmp 

COPY ./ui /app/
COPY .streamlit /app/.streamlit

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "./main.py", "--server.port=8501", "--server.address=0.0.0.0"]