# Get started

## Install minikube

[minikube](https://minikube.sigs.k8s.io/) _"quickly sets up a local Kubernetes cluster on macOS, Linux, and Windows"_. Follow the [_Get Started!_](https://minikube.sigs.k8s.io/docs/start/) guide to install and configure minikube.

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

## Start the engine

In the [engine](../engine) directory, build the Engine Docker image with the following commands. You might need to create and use a Personal Access Token (PAT) to login to the remote Docker container registry.

See more about the Minikube Docker environment here: [minikube.sigs.k8s.io - Pushing images](https://minikube.sigs.k8s.io/docs/handbook/pushing/).

```sh
# Access the Minikube's Docker environment
eval $(minikube docker-env)

# Login to the remote Docker container registry
docker login registry.forge.hefr.ch --user <GitLab user> --password-stdin

# Build the Docker image
docker build -t csia-pme/engine .

# Exit the Minikube's Docker environment
eval $(minikube docker-env -u)
```

In the [engine](../engine) directory, start the Engine with the following commands.

```sh
# Start MinIO
kubectl apply \
    -f kubernetes/minio.pvc.yml \
    -f kubernetes/minio.service.yml \
    -f kubernetes/minio.pod.yml

# Start Mongo
kubectl apply \
    -f kubernetes/mongo.pvc.yml \
    -f kubernetes/mongo.service.yml \
    -f kubernetes/mongo.pod.yml

# Start the engine
kubectl apply \
    -f kubernetes/engine.service.yml \
    -f kubernetes/engine.pod.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel
```

Access the Engine documentation on [http://localhost:8080/docs](http://localhost:8080/docs).

Access the MinIO console on [http://localhost:9001](http://localhost:9001).

## Start a machine learning backend

A machine learning backend is a service that will register to the Engine in order to accept tasks to execute.

_TODO_
