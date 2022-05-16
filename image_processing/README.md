# API
Input
 - Exemple : 127.0.0.1:8080/compute?areas=%22%5B%5B72%2C%2036%2C%20122%2C%20107%5D%5D%22&callback_url=http%3A%2F%2F127.0.0.1%3A8083
   
    With an image as [ Content-Type : multipart/form-data ] => { "img": image_bytes }
 - areas : a list containing possibly multiple faces coordinates, which is described as a list of 4 coordinates
 
    [[10, 15, 40, 70]]

Output
 - Exemple : params={"task_id": task_id}, json={"areas": task["areas"]}, files={"result": task["result"]}
 - areas : a list containing possibly multiple faces coordinates, which is described as a list of 4 coordinates

    [[10, 15, 40, 70]]
 - result : a multipart image with blur effects on
 
    [ Content-Type : multipart/form-data ] => { "img": image_bytes }

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

APP_HOST=0.0.0.0 APP_PORT=8081 APP_SERVICE=http://192.168.x.x:8081 APP_ENGINE=http://192.168.x.x:8080 APP_LOG=info python3 ./area_blur/main.py

```

## Run using docker

First build the dockerfile which you can find in the root directory and build it in the same directory using the following command :

```bash
docker build -t pi/area_blur -f dockerfile .
```

Then run it using the following command and don't forget to add the two required arguments at the end as the entrypoint of the docker file is the command to run the API :

```bash
docker run -it --rm -p8080:8080 pi/area_blur
```

or

```bash
docker run -it --env APP_HOST=0.0.0.0 --env APP_PORT=4040 --env APP_LOG=info --env APP_ENGINE=http://engine.com/notify --rm -p8080:4040 pi/area_blur
```
