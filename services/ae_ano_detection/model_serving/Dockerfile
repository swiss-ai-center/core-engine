FROM ghcr.io/csia-pme/csia-pme-base-image:latest
<<<<<<< refs/remotes/origin/main:services/ae_anno_detection/model_serving/Dockerfile
COPY ./requirements.txt /tmp/requirements.txt
=======
COPY requirements.txt /tmp/requirements.txt
>>>>>>> Update for new engine:services/ae_ano_detection/model_serving/Dockerfile
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir /app
COPY main.py /app
COPY api /app/api

<<<<<<< refs/remotes/origin/main:services/ae_anno_detection/model_serving/Dockerfile
ENTRYPOINT [ "python3", "/app/main.py"]
=======
WORKDIR /app

ENTRYPOINT [ "python3", "/app/main.py" ]
>>>>>>> Update for new engine:services/ae_ano_detection/model_serving/Dockerfile
