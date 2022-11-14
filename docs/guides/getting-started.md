# Getting started

This page will guide you through the steps to run the project locally.

## Install Docker

[Docker](https://docker.com/) _"delivers software in packages called containers"_. Follow the [_Install Docker Engine_ - docs.docker.com](https://docs.docker.com/engine/install/) guide to install and configure Docker.

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

_Follow the instructions described in the [Engine documention - Run locally using Kubernetes (with minikube) and official Docker images](../engine/readme.md#run-locally-using-kubernetes-with-minikube-and-official-docker-images)._

## Start the Webapp

_Follow the instructions described in the [Webapp documention - Run locally using Kubernetes (with minikube) and a local Docker image](../webapp/readme.md#run-locally-using-kubernetes-with-minikube-and-a-local-docker-image)._

## Start a machine learning service

A machine learning service is a service that will register to the Engine in order to accept tasks to execute.

Refer to the [Services](../services/readme.md) documentation for all the available machine learning backend services.

### `average_shade` service

_Follow the instructions described in the [average_shade documention - Run locally using Kubernetes (with minikube) and official Docker images](../services/average-shade.md#run-locally-using-kubernetes-with-minikube-and-official-docker-image)._

### `digit_recognition` service

_Follow the instructions described in the [digit_recognition documention - Run locally using Kubernetes (with minikube) and official Docker images](../services/digit-recognition.md#run-locally-using-kubernetes-with-minikube-and-official-docker-image)._

### `face_analyzer` backend

_Follow the instructions described in the [digit_recognition documention - Run locally using Kubernetes (with minikube) and official Docker images](../services/face-analyzer.md#run-locally-using-kubernetes-with-minikube-and-official-docker-image)._

### `face_detection` backend

_Follow the instructions described in the [face_detection documention - Run locally using Kubernetes (with minikube) and official Docker images](../services/face-detection.md#run-locally-using-kubernetes-with-minikube-and-official-docker-image)._

### `image_processing` backend

_Follow the instructions described in the [image_processing documention - Run locally using Kubernetes (with minikube) and official Docker images](../services/image-processing.md#run-locally-using-kubernetes-with-minikube-and-official-docker-image)._
