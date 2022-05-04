Mettre pydantic
Swagger
Expliquer comment run

# How to run

Using both docker or your local python3, the API require at least the two first following arguments :

- `--listen` : str - It's the address on which the API will listen. Put `0.0.0.0` for it to listen for every request.
- `--port` : int - It's the port the API will listen on. For standard HTTP, use `80`.
- `--reload` : Optionnal - Write `--reload` for the API to reload itself after applying changes to the code. Use it in dev only.

## Run your machine without docker

First, install the requirements using `pip3`

```bash
pip3 install -r requirements.txt
```

Then, you can run the following command to run it in dev :

```bash
python3 api/api.py --port 80 --listen 0.0.0.0 --reload
# Reload is optionnal, it's is practical to use it when you have to change code a lot, the API reload itself when saving the file.
```

## Run using docker

First build the dockerfile which you can find in the root directory and build it in the same directory using the following command :

```bash
docker build -t pi/api -f dockerfile .
```

Then run it using the following command and don't forget to add the two required arguments at the end as the entrypoint of the docker file is the command to run the API :

```bash
docker run -it --rm -p80:80 pi/api --listen 0.0.0.0 --port 80
```

If you wish to use the reload while in the docker, mount a volume linking you local file to the ones in the docker :

```bash
docker run -it --rm -p80:80 -v$(pwd)/api:/app/api pi/api --listen 0.0.0.0 --port 80 --reload
```

## Running the tests

### On your local machine

To run the tests of you API make sur you are in the root directory of the project and run the following command :

```bash
python3 -m pytest api/tests
```

### Inside the docker

TBD

# Routes

**GET /docs**
This route will show you the full documentation of all your routes.

**GET /static/file1.txt**
This route will return a static file text file.

**GET /**
This route will redirect you on `/hello`.

**GET /hello**
This route will return you a JSON object with the following format :

```json
{
  "Hello": "World !"
}
```

**GET /pydantic**
This route require parameters in the body and will return you the object you gave him as JSON.

Here is the Pydantic model `GExample` where the field `name` is required and the field `surename` is optional :

```python
from pydantic import BaseModel
from typing import Optional
class GExample (BaseModel):
	name: str
	surname: Optional[str]
```

With this declaration, you can call the API using either both parameter, or only the name :

```bash
# With both parameters
curl -X 'GET' \
  'http://localhost/pydantic' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My name is awesome :D !",
  "surname": "I have a surename, WoW !"
}'
```

```bash
# With only one of the required parameters
curl -X 'GET' \
  'http://localhost/pydantic' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "My name is awesome :D !"
}'
```

**POST /pydantic**
This route require parameters in the body and will return you the object you gave him as JSON.

Here is the Pydantic model `PExample` where the field `name` is required and the field `surename` is optional :

```python
from pydantic import BaseModel
from models.GExample import GExample
# Example for a POST request
class PExample(BaseModel):
	email : str
	age: int
	basicInfo: GExample
```

With this declaration, you can call the API using either both parameter of the `GModel`, or only with one. But the `email` and `age` are required :

```bash
curl -X 'POST' \
  'http://localhost/pydantic' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "ihave@nema.il",
  "age": 23,
  "basicInfo": {
    "name": "My name is awesome :D !",
    "surname": "I have a surename, WoW !"
  }
}'
```

# Execute tests

Execute at the root of the project the following command :

```bash
python3 -m pytest api/tests
```
