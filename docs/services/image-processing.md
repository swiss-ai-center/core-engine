# image_processing

- [Code](../../services/image_processing/README.md)
- average_shape URL when run locally: <http://localhost:8181/docs>
- average_shape URL when deployed on Fribourg's Kubernetes: <https://image-processing-csia-pme.kube.isc.heia-fr.ch/docs>

## Description

This service provides generic image processing features, such as blurring, cropping, resizing etc... This service uses Pillow and opencv.

## How to run

### Environment variables

The service will use the following environment variables if defined.

*General variables*

- `APP_HOST`: address on which the API will listen, default is 127.0.0.1
- `APP_PORT`: port the API will listen on, default is 8080
- `APP_LOG`: log level, default is info
- `APP_ENGINE`: the url to the engine, if provided, the service will announce itself to the engine periodically
- `APP_SERVICE`: the url of the service itself, needed to announce correct routes to the engine
- `APP_NOTIFY_CRON`: the frequency in second of the heartbeat announce to the engine, default is 30

### Start the application

In the [image_processing](../../services/image_processing) directory, start the service with the following commands.

Generate the virtual environment and install the dependencies.

```sh
# Generate the virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the requirements
pip install --requirement requirements.txt
```

Start the application.

```sh
# Start the application
APP_HOST=0.0.0.0 APP_PORT=8181 APP_ENGINE=http://localhost:8080 APP_SERVICE=http://localhost:8181 python3 main.py
```

Access the `image_processing` documentation on <http://localhost:8181/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### Run the tests

In the [image_processing](../../services/image_processing) directory, run the tests with the following commands.

Install the additional packages.

```sh
# Install required packages for testing
pip3 install pytest pytest-asyncio aiofile
```

Run the tests.

```sh
# Run the tests
python3 -m pytest --asyncio-mode=auto
```

### Run locally using Kubernetes (with minikube) and official Docker images

Start the service with the following commands. This will start the service with the official Docker images that are hosted on GitHub.

In the [image_processing](../../services/image_processing) directory, start the service with the following commands.

```sh
# Start the image_processing backend
kubectl apply \
    -f kubernetes/image-processing.config-map.yml \
    -f kubernetes/image-processing.stateful.yml \
    -f kubernetes/image-processing.service.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine. The terminal in which the tunnel is created must stay open.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel --bind-address 127.0.0.1
```

Access the `image_processing` documentation on <http://localhost:8181/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### Run locally using Kubernetes (with minikube) and a local Docker image

**Note**: The service StatefulSet (`image-processing.stateful.yml` file) must be deleted and recreated every time a new Docker image is created.

Start the service with the following commands. This will start the service with the a local Docker image for the service.

In the [image_processing](../../services/image_processing) directory, build the Docker image with the following commands.

```sh
# Access the Minikube's Docker environment
eval $(minikube docker-env)

# Build the Docker image
docker build -t ghcr.io/csia-pme/csia-pme-image-processing:latest .

# Exit the Minikube's Docker environment
eval $(minikube docker-env -u)

# Edit the `kubernetes/image-processing.stateful.yml` file to use the local image by uncommented the line `imagePullPolicy`
#
# From
#
#        # imagePullPolicy: Never
#
# To
#
#        imagePullPolicy: Never
```

In the [image_processing](../../services/image_processing) directory, start the service with the following commands.

```sh
# Start the image_processing backend
kubectl apply \
    -f kubernetes/image-processing.config-map.yml \
    -f kubernetes/image-processing.stateful.yml \
    -f kubernetes/image-processing.service.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine. The terminal in which the tunnel is created must stay open.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel --bind-address 127.0.0.1
```

Access the `image_processing` documentation on <http://localhost:8181/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.
