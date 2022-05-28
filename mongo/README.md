# Description
This folder contains the definition of the mongodb service that runs in the cluster and is used by the engine, alongside example usage code.

# How to run

Then run it:
```bash
docker run -it --rm -p 27017:27017 pi/mongo
```

You can then run a simple python test after installing the requirements :
```bash
pip3 install -r requirements.txt
python3 test.py
```

## Run using docker
### Build docker image
The mongo docker image can be built using the dockerfile using the command:

```bash
docker build -t pi/mongo -f dockerfile .
```

### Run
Then it can be run normally:

```bash
docker run -it --rm -p 27017:27017 pi/mongo
```

## Use
The mongo server is set up using the `init.js` script, including the credentials to use it. Then, the mongo server can be used with the URI "mongodb://MONGOUSER:MONGOPASSWD@HOST:PORT".
