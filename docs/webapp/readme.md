# Webapp

- [Code](../../webapp)
- Webapp URL when run locally: <http://localhost:8686>
- Webapp URL when deployed on Fribourg's Kubernetes: <https://webapp-csia-pme.kube.isc.heia-fr.ch/docs>

## Description

This service allows to visualize services and pipelines from the [Engine](../engine/readme.md). This service was built and tested with React.

## How to run

### Environment variables

The service will use the following environment variables if defined.

*General variables*

- `REACT_APP_ENGINE_URL`: The Engine URL

**Note**: The environment variables are replaced while building the React application.

## Run the application

In the [webapp](../../webapp) directory, start the Webapp with the following commands.

```sh
# Install the dependencies
npm ci --legacy-peer-deps

# Optional: Edit the environment variables to change the Engine URL
vim .env

# Start the Webapp
npm run start
```

A browser should open on <http://localhost:3000> with the Webapp running and querying the Engine.

## Build the application

In the [webapp](../../webapp) directory, build the Webapp with the following commands.

```sh
# Install the dependencies
npm ci --legacy-peer-deps

# Build the Webapp
npm run build
```

The output of the build is in the [build](../../webapp/build) directory.

Once a React application is built, the environment variables cannot be changed.

## Build and run the Docker image

In order to build the Docker image, the application must be [built](#build-the-application) beforehand. Then, the Docker image can be built with the following commands.

```sh
# Build the Docker image with a tag
docker build -t csia-pme/webapp .

# Run the Docker image
docker run -p 8686:80 csia-pme/webapp
```

The Webapp is available on <http://localhost:8686>.

> **Q**: _Why don't we build the React application within the Docker image?_\
> **A**: This setup allows us to speed up the build process of the Docker image: it does not need to download and install all dependencies every time the `package.json` file is updated. In a CI/CD set up, the `node_modules` can be cached in the `build` stage and the output can be passed to the `publish` stage.

### Run locally using Kubernetes (with minikube) and official Docker images

Start the Webapp with the following commands. This will start the Webapp with the official Docker images that are hosted on GitHub.

In the [webapp](../../webapp) directory, start the Webapp with the following commands.

```sh
# Start the webapp
kubectl apply \
    -f kubernetes/webapp.config-map.yml \
    -f kubernetes/webapp.stateful.yml \
    -f kubernetes/webapp.service.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine. The terminal in which the tunnel is created must stay open.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel --bind-address 127.0.0.1
```

Access the Webapp on <http://localhost:8686>.

### Run locally using Kubernetes (with minikube) and a local Docker image

**Note**: The service StatefulSet (`webapp.stateful.yml` file) must be deleted and recreated every time a new Docker image is created.

Start the service with the following commands. This will start the service with the a local Docker image for the service.

In the [webapp](../../services/webapp) directory, build the Docker image with the following commands.

```sh
# Install Node dependencies
npm ci --legacy-peer-deps

# Optional: Edit the environment variables to change the Engine URL
vim .env

# Build the Webapp
npm run build

# Access the Minikube's Docker environment
eval $(minikube docker-env)

# Build the Docker image
docker build -t ghcr.io/csia-pme/csia-pme-webapp:latest .

# Exit the Minikube's Docker environment
eval $(minikube docker-env -u)

# Edit the `kubernetes/webapp.stateful.yml` file to use the local image by uncommented the line `imagePullPolicy`
#
# From
#
#        # imagePullPolicy: Never
#
# To
#
#        imagePullPolicy: Never
```

In the [webapp](../../services/webapp) directory, start the service with the following commands.

```sh
# Start the webapp backend
kubectl apply \
    -f kubernetes/webapp.config-map.yml \
    -f kubernetes/webapp.stateful.yml \
    -f kubernetes/webapp.service.yml
```

Create a tunnel to access the Kubernetes cluster from the local machine. The terminal in which the tunnel is created must stay open.

```sh
# Open a tunnel to the Kubernetes cluster
minikube tunnel --bind-address 127.0.0.1
```

Access the Webapp on <http://localhost:8686>.
