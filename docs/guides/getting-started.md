# Getting started

This page will guide you through the steps to run the project locally.

## Install Docker

[Docker](https://minikube.sigs.k8s.io/) _"delivers software in packages called containers"_. Follow the [_Install Docker Engine_ - docs.docker.com](https://docs.docker.com/engine/install/) guide to install and configure Docker.

## Install minikube

[minikube](https://minikube.sigs.k8s.io/) _"quickly sets up a local Kubernetes cluster on macOS, Linux, and Windows"_. Follow the [_Get Started!_ - minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) guide to install and configure minikube.

## Kubernetes tips

To visualize pods (= containers), use the following command.

```sh
# View pods
kubectl get pods
```

To visualize pod's logs, use the following command.

```sh
# View pod's logs
kubectl logs <name of the pod>

# or

# Follow the pod's logs (CTRL+C to exit)
kubectl logs --follow <name of the pod>
```

## Start minikube

In order to start minikube, execute the following command.

```sh
# Start minikube
minikube start
```

Validate minikube has successfully started with the following command.

```sh
# Validate minikube has started
kubectl get pods --all-namespaces
```

## Start the Engine

In the [engine](../../engine) directory, start the Engine with the following commands.

```sh
# Start MinIO
kubectl apply \
    -f kubernetes/minio.pvc.yml \
    -f kubernetes/minio.config-map.yml \
    -f kubernetes/minio.stateful.yml \
    -f kubernetes/minio.service.yml

# Start Mongo
kubectl apply \
    -f kubernetes/mongo.pvc.yml \
    -f kubernetes/mongo.config-map.yml \
    -f kubernetes/mongo.stateful.yml \
    -f kubernetes/mongo.service.yml

# Start the engine
kubectl apply \
    -f kubernetes/engine.config-map.yml \
    -f kubernetes/engine.stateful.yml \
    -f kubernetes/engine.service.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine. The terminal in which the tunnel is created must stay open.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel --bind-address 127.0.0.1
```

Access the Engine documentation on <http://localhost:8080/docs>.

Access the MinIO console on <http://localhost:9001>.

## Start the Webapp

In the [webapp](../../webapp) directory, build the Docker image with the following commands.

```sh
# Access the Minikube's Docker environment
eval $(minikube docker-env)

# Build the Docker image
docker build --build-arg ENGINE_URL="http://localhost:8080" -t csia-pme/webapp .

# Exit the Minikube's Docker environment
eval $(minikube docker-env -u)
```

In the [webapp](../../webapp) directory, start the Webapp with the following commands.

```sh
# Start the webapp
kubectl apply \
    -f kubernetes/webapp.service.yml \
    -f kubernetes/webapp.pod.yml
```

Access the Webapp on <http://localhost:8686>.

When new machine learning backends are added to the Engine, they will be available in the Webapp.

## Start a machine learning service

A machine learning service is a service that will register to the Engine in order to accept tasks to execute.

Refer to the [Services](../services/index.md) documentation for all the available machine learning backend services.

### `average_shade` service

In the [average_shade](../../services/average_shade) directory, start the machine learning backend with the following commands.

```sh
# Start the average_shade backend
kubectl apply \
    -f kubernetes/average-shade.config-map.yml \
    -f kubernetes/average-shade.stateful.yml \
    -f kubernetes/average-shade.service.yml
```

Access the `average_shade` documentation on <http://localhost:8282/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### `digit_recognition` service

In the [digit_recognition/model_creation](../../services/digit_recognition/model_creation) directory, build the model with the following commands.

```sh
# Export the MinIO S3 credentials (ask them to other members of the team)
export AWS_ACCESS_KEY_ID=***
export AWS_SECRET_ACCESS_KEY=***

# Pull the required data for the experiment from MinIO
dvc pull

# Force the reproduction of the experiment
dvc repro --force
```

In the [digit_recognition/model_creation](../../services/digit_recognition/model_creation) directory, copy the built model to the [digit_recognition/model_serving](../../services/digit_recognition/model_serving) directory with the following commands.

```sh
# Copy the model to the serving directory
cp mnist_model.h5 ../model_serving
```

In the [digit_recognition/model_serving](../../services/digit_recognition/model_serving) directory, start the machine learning backend with the following commands.

```sh
# Start the digit_recognition backend
kubectl apply \
    -f kubernetes/digit-recognition.config-map.yml \
    -f kubernetes/digit-recognition.stateful.yml \
    -f kubernetes/digit-recognition.service.yml
```

Access the `digit_recognition` documentation on <http://localhost:8383/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### `face_analyzer` backend

In the [face_analyzer](../../services/face_analyzer) directory, start the machine learning backend with the following commands.

```sh
# Start the face_analyzer backend
kubectl apply \
    -f kubernetes/face-analyzer.config-map.yml \
    -f kubernetes/face-analyzer.stateful.yml \
    -f kubernetes/face-analyzer.service.yml
```

Access the `face_analyzer` documentation on <http://localhost:8484/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### `face_detection` backend

In the [face_detection](../../services/face_detection) directory, start the machine learning backend with the following commands.

```sh
# Start the face_detection backend
kubectl apply \
    -f kubernetes/face-detection.config-map.yml \
    -f kubernetes/face-detection.stateful.yml \
    -f kubernetes/face-detection.service.yml
```

Access the `face_detection` documentation on <http://localhost:8585/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.

### `image_processing` backend

In the [image_processing](../../services/image_processing) directory, start the machine learning backend with the following commands.

```sh
# Start the image_processing backend
kubectl apply \
    -f kubernetes/image-processing.config-map.yml \
    -f kubernetes/image-processing.stateful.yml \
    -f kubernetes/image-processing.service.yml
```

Access the `image_processing` documentation on <http://localhost:8181/docs>.

Access the Engine documentation on <http://localhost:8080/docs> to validate the backend has been successfully registered to the Engine.
