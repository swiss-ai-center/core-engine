# MongoDB

DO NOT HESITATE TO UPDATE OR DISCUSS THE DESCRIBED STRUCTURE

# How to run

First build the dockerfile :
```bash
docker build -t pi/mongo -f dockerfile .
```

Then run it:
```bash
docker run -it --rm -p 27017:27017 pi/mongo
```

You can then run a simple python test after installing the requirements :
```bash
pip3 install -r requirements.txt
python3 test.py
```

# Environment variable

The driver will try to use the os environment variable to set itself. If the following variable do not exists the content in the constructor will be used
```bash
export MONGO_USERNAME=registry
export MONGO_PASSWORD=PiRegistry_2022
export MONGO_HOST=127.0.0.1
export MONGO_PORT=27017
export MONGO_AUTHDB=Registry
```