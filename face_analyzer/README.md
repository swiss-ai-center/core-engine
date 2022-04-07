# How to run

Using both docker or your local python3, the worker will use the following environment variables if defined:

- APP_HOST: address on which the API will listen, default is 127.0.0.1
- APP_PORT: port the API will listen on, default is 8080
- APP_LOG: log level, default is info
- APP_ENGINE: url to the engine notify endpoint, default is none

## Run your machine without docker

First, install the requirements using `pip3`

```bash
pip3 install -r requirements.txt
```

Then, you can run the following command to run it in dev :

```bash
python3 main.py
```

or with all custom parameters:

```bash
APP_HOST=0.0.0.0 APP_PORT=4040 APP_LOG=info APP_ENGINE=http://engine.com/notify python3 main.py
```

## Run using docker

First build the dockerfile which you can find in the root directory and build it in the same directory using the following command :

```bash
docker build -t pi/worker_example -f dockerfile .
```

Then run it using the following command and don't forget to add the two required arguments at the end as the entrypoint of the docker file is the command to run the API :

```bash
docker run -it --rm -p8080:8080 pi/worker_example
```

or

```bash
docker run -it --env APP_HOST=0.0.0.0 --env APP_PORT=4040 --env APP_LOG=info --env APP_ENGINE=http://engine.com/notify --rm -p8080:4040 pi/worker_example
```
