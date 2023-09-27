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

## Start the Core Engine

_Follow the instructions described in the [Core Engine documentation - Run locally using Kubernetes (with minikube) and official Docker images](../reference/core-engine.md)._

## Start the Webapp

_Follow the instructions described in the [Webapp documentation - Run locally using Kubernetes (with minikube) and a local Docker image](../reference/webapp.md)._

## Start a machine learning service

A machine learning service is a service that will register to the Core Engine in order to accept tasks to execute.

Refer to the [Services](../reference/index.md#services) documentation for all the available machine learning backend services.
