# Webapp

- [Code](../../webapp)
- Access when deployed locally: <http://localhost:8686>

## Description

This service allows to visualize services and pipelines from the [Engine](../engine/readme.md). This service was built and tested with React.

## Develop locally

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

### Run locally using Kubernetes

Refer to the [Getting started](../guides/getting-started.md) guide in order to run this service locally.
