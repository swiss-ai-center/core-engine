# Description
This repository contains all code for the *PI-AIMarketplace* project.

# CI/CD
The CI/CD pipelines are defined using the Gitlab CI syntax. The main `.gitlab-ci.yml` defines basic stages and includes specific definitions in each service. Currently, the following stages are defined:

- *lint*: runs `flake8` to check the code style
- *prepare*: run service specific script before the build, like downloading ML models
- *test*: run the unit testing
- *build*: create the docker image and push it in the registry
- *deploy*: applies the changes on the Kubernetes cluster

The CI/CD pipeline is triggered on each individual service only if a merge request modifies its content. Currently, we only have one running cluster, but a good practice would be to have multiple environments, like `dev`, `test` and `prod` which are deployed when according branches are modified.

# Services
Each service can be used either on its own or integrated in the cluster.

- [digit_recognition](digit_recognition): Recognize a digit in an image using machine learning
- [engine](engine): Pipeline manager and scheduler, allows to create complex jobs by using all other services of teh cluster
- [face_analyzer](face_analyzer): Analyzes a face in an image and guesses age, gender, race and emotion using machine learning
- [face_detection](face_detection): Returns bounding boxes of all faces detected in an image using machine learning
- [image_processing](image_processing): General image processing service that allows to do basic operations like blur, crop, resize etc...
- [mongo](mongo): Mongo database server used to store pipelines and jobs
- [webapp](webapp): Frontend of the system, contains a user friendly interface that allows to see available pipelines and run jobs

# Service structure
The basic structure of a service is very simple, so adding new services is really easy and painless. Every service has:

- `requirements.txt`: list of python packages needed to run the service, usually obtained by running `pip freeze`
- `SERVICENAME.gitlab-ci.yml`: service specific definitions for the CI/CD
- `dockerfile`: docker recipe to build the docker image
- `main.py`: entrypoint of the service, usually not to be modified
- `kubernetes/`: folder containing the Kubernetes configuration for this service
- `api/api.py`: http layer definition of the service, FastAPI engine and all living objects are instanciated here
- `api/cron.py`: simple timer object, used by default to send heartbeat requests to the engine
- `api/worker.py`: contains the definition of 2 non-blocking, async workers. One contains the business code and the other returns the result as callback.
- `api/interface.py`: contains basic enums and engine specific API definition

# How to run
The CD pipeline allows to automatically deploy the services in our Kubernetes cluster. However, each service can also run natively or in docker by building the docker image, or directly using the images in the local docker registry. Please, refer to the documentation of each service to run or build its image.
