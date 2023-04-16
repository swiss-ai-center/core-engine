### Service with a model

In this section, you will create a service that uses a model.

#### 1.1 Get the source code

First, you can download or clone the source code from the [CSIA-PME service templates repository](https://github.com/csia-pme/services-templates).

In this tutorial, we will implement a service that does require a model, so we will use the `sample-service-with-model` template.

Open your terminal and copy the content of the template to a new folder called `ano-detection`. Then go inside it.

```bash
cp -r sample-service-without-model ano-detection
cd detection
```

#### 1.2 Create a virtual environment

Instead of installing the dependencies globally, it is recommended to create a virtual environment.

To create a virtual environment, run the following command inside the project folder:

```sh
python3.10 -m venv .venv
```

Then, activate the virtual environment:

```sh
source .venv/bin/activate
```

#### 1.3 Install the dependencies

For the service to work we will need to install some dependencies of the template.
So edit the `requirements.txt` file and add the following lines:

```txt hl_lines="2 3"
common-code[test] @ git+https://github.com/csia-pme/csia-pme.git@main#subdirectory=common-code
matplotlib==3.6.3
numpy==1.24.2
pandas==1.5.3
scikit-learn==1.2.1
tensorflow==2.9.0
```

Then, install the dependencies:

```sh
pip install -r requirements.txt
```
This will install the default service dependencies and the ones we just added.

#### 1.4 Implement the service

##### 1.4.1 Update the README

Open the `README.md` file and update the title and the description of the service.

```md
# Anomaly detection

This service detects anomalies in a time series.
```

##### 1.4.2 Update the service kubernetes configuration

In the `kubernetes` folder, you will find the configuration files for the service.

Rename all the files by replacing `sample-service` with `ano-detection`.

```
ano-detection
├── kubernetes
│   ├── ano-detection.config-map.yaml
│   ├── ano-detection.ingress.yaml
│   ├── ano-detection.service.yaml
│   └── ano-detection.stateful.yaml
└── ...
```

Open the `ano-detection.config-map.yaml` file and update `sample-service` with `ano-detection`.

```yaml hl_lines="5 8 15"
apiVersion: v1
kind: ConfigMap
metadata:
  # TODO: 1. CHANGE THE NAME OF THE CONFIG MAP (1)!
  name: ano-detection-config
  labels:
    # TODO: 2. CHANGE THE APP LABEL (2)!
    app: ano-detection
data:
  ENVIRONMENT: development
  LOG_LEVEL: debug
  ENGINE_URL: http://engine-service:8080
  # TODO: 3. CHANGE THE SERVICE URL (3)!
  # (the port must be the same as in the sample-service.service.yml and unused by other services)
  SERVICE_URL: http://ano-detection-service:8001
```

1. Change the name of the config map to `ano-detection-config`
2. Change the app label to `ano-detection`
3. Change the service url to `http://ano-detection-service:8001`. The port must be the same as in the `ano-detection.service.yaml` and unused by other services. (this is for local development only)

Open the `ano-detection.ingress.yaml` file and update `sample-service` with `ano-detection`.

```yaml hl_lines="5 12 20 26"
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  # TODO: 1. CHANGE THE NAME OF THE INGRESS (1)!
  name: ano-detection-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "16m"
    nginx.org/client-max-body-size: "16m"
spec:
  rules:
  # TODO: 2. CHANGE THE HOST (2)!
  - host: ano-detection-csia-pme.kube.isc.heia-fr.ch
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            # TODO: 3. CHANGE THE NAME OF THE SERVICE (3)!
            name: ano-detection-service
            port:
              number: 80
  tls:
    - hosts:
        # TODO: 4. CHANGE THE HOST (4)!
        - ano-detection-csia-pme.kube.isc.heia-fr.ch
```

1. Change the name of the ingress to `ano-detection-ingress`
2. Change the host to `ano-detection-csia-pme.kube.isc.heia-fr.ch`
3. Change the name of the service to `ano-detection-service`
4. Change the host to `ano-detection-csia-pme.kube.isc.heia-fr.ch`

!!! info "Note"
    The host can be changed to your own domain name if the service is deployed on another Kubernetes cluster.

Open the `ano-detection.service.yaml` file and update `sample-service` with `ano-detection`.

```yaml hl_lines="5 11 16"
apiVersion: v1
kind: Service
metadata:
  # TODO: 1. CHANGE THE NAME OF THE SERVICE (1)!
  name: ano-detection-service
spec:
  type: LoadBalancer
  ports:
    - name: http
      # TODO: 2. CHANGE THE PORT (must be the same as in the sample-service.config-map.yml) (2)!
      port: 8001
      targetPort: 80
      protocol: TCP
  selector:
    # TODO: 3. CHANGE THE APP LABEL (3)!
    app: ano-detection
```

1. Change the name of the service to `ano-detection-service`
2. Change the port to `8001`. The port must be the same as in the `ano-detection.config-map.yaml` and unused by other services. (this is for local development only)
3. Change the app label to `ano-detection`

Open the `ano-detection.stateful.yaml` file and update `sample-service` with `ano-detection`.

```yaml hl_lines="6 9 12 17 22 26 28 44"
apiVersion: apps/v1
kind: StatefulSet
metadata:
  # This name uniquely identifies the stateful set
  # TODO: 1. CHANGE THE NAME OF THE STATEFUL SET (1)!
  name: sample-service-stateful
  labels:
    # TODO: 2. CHANGE THE APP LABEL (2)!
    app: sample-service
spec:
  # TODO: 3. CHANGE THE NAME OF THE SERVICE (3)!
  serviceName: sample-service
  replicas: 1
  selector:
    matchLabels:
      # TODO: 4. CHANGE THE APP LABEL (4)!
      app: sample-service
  template:
    metadata:
      labels:
        # TODO: 5. CHANGE THE APP LABEL (5)!
        app: sample-service
    spec:
      containers:
      # TODO: 6. CHANGE THE NAME OF THE CONTAINER (6)!
      - name: sample-service
        # TODO: 7. CHANGE THE IMAGE NAME (7)!
        image: ghcr.io/csia-pme/csia-pme-sample-service:latest
        # If you build the image locally, change the next line to `imagePullPolicy: Never` - there is no need to pull the image
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 80
        env:
        - name: MAX_TASKS
          value: "50"
        - name: ENGINE_ANNOUNCE_RETRIES
          value: "5"
        - name: ENGINE_ANNOUNCE_RETRY_DELAY
          value: "3"
        envFrom:
          - configMapRef:
              # TODO: 8. CHANGE THE NAME OF THE CONFIG MAP (8)!
              name: sample-service-config
```

1. Change the name of the stateful set to `ano-detection-stateful`
2. Change the app label to `ano-detection`
3. Change the name of the service to `ano-detection`
4. Change the app label to `ano-detection`
5. Change the app label to `ano-detection`
6. Change the name of the container to `ano-detection`
7. Change the image name to `ghcr.io/csia-pme/csia-pme-ano-detection-service:latest`
8. Change the name of the config map to `ano-detection-config`

!!! warning "TODOs"
    When you are done, you need to remove all the TODOs from the files.

##### 1.4.3 Update the service code

First open the `.env` file and update the `SERVICE_URL` variable to `http://localhost:8001`. The port must be the same as in the `ano-detection.config-map.yaml` file.

```bash hl_lines="12"
# Log level
LOG_LEVEL=debug

# Environment
ENVIRONMENT=development

# The Engine URL
ENGINE_URL="http://localhost:8080"

# The Service URL
# TODO: 1. REPLACE THE PORT WITH THE SAME AS IN THE CONFIG-MAP FILE (1)!
SERVICE_URL="http://localhost:8001"

# The maximum of tasks the service can process
MAX_TASKS=50

# The number of times the service tries to announce itself to the Engine
ENGINE_ANNOUNCE_RETRIES=5

# The number of seconds between each retry
ENGINE_ANNOUNCE_RETRY_DELAY=3
```

1. Replace the port with the same as in the `ano-detection.config-map.yaml` file.

All the code of the service is in the `main.py` file.

Open the `main.py` with your favorite editor and follow the instructions below.

```py hl_lines="20-22 29-31 39-40 46-52 56-83 87-92 97-112"
import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from common_code.config import get_settings
from pydantic import Field
from common_code.http_client import HttpClient
from common_code.logger.logger import get_logger
from common_code.service.controller import router as service_router
from common_code.service.service import ServiceService
from common_code.storage.service import StorageService
from common_code.tasks.controller import router as tasks_router
from common_code.tasks.service import TasksService
from common_code.service.models import Service, FieldDescription
from common_code.service.enums import ServiceStatus, FieldDescriptionType

# Imports required by the service's model
# TODO: 1. ADD REQUIRED IMPORTS (ALSO IN THE REQUIREMENTS.TXT) (1)!
import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import io

settings = get_settings()


class MyService(Service):
    # TODO: 2. CHANGE THIS DESCRIPTION (2)!
    """
    Anomaly Detection model
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    def __init__(self):
        super().__init__(
            # TODO: 3. CHANGE THE SERVICE NAME AND SLUG (3)!
            name="Anomaly Detection",
            slug="ano-detection",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            # TODO: 4. CHANGE THE INPUT AND OUTPUT FIELDS (4)!
            data_in_fields=[
                FieldDescription(name="text", type=[FieldDescriptionType.TEXT_CSV, FieldDescriptionType.TEXT_PLAIN]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.IMAGE_PNG]),
            ]
        )
        self.model = tf.keras.models.load_model("../model/ae_model.h5")

    # TODO: 5. CHANGE THE PROCESS METHOD (CORE OF THE SERVICE) (5)!
    async def process(self, data):
        # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
        raw = str(data["text"].data)[2:-1]
        raw = raw.replace('\\t', ',').replace('\\n', '\n').replace('\\r', '\n')
        X_test = pd.read_csv(io.StringIO(raw), dtype={"value": np.float64})

        # Use the model to reconstruct the original time series data
        reconstructed_X = self.model.predict(X_test)

        # Calculate the reconstruction error for each point in the time series
        reconstruction_error = np.square(X_test - reconstructed_X).mean(axis=1)

        err = X_test
        fig, ax = plt.subplots(figsize=(20, 6))

        a = err.loc[reconstruction_error >= np.max(reconstruction_error)]  # anomaly

        ax.plot(err, color='blue', label='Normal')

        ax.scatter(a.index, a, color='red', label='Anomaly')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "result": TaskData(data=buf.read(), type=FieldDescriptionType.IMAGE_PNG)
        }


# TODO: 6. CHANGE THE API DESCRIPTION AND SUMMARY (6)!
api_description = """
Rotate an image by 90 degrees clockwise depending on the value of the `rotation` parameter. (90, 180, 270)
"""
api_summary = """
Rotate an image by 90 degrees clockwise.
"""

# Define the FastAPI application with information
# TODO: 7. CHANGE THE API TITLE, VERSION, CONTACT AND LICENSE (7)!
app = FastAPI(
    title="Anomaly Detection API.",
    description=api_description,
    version="0.0.1",
    contact={
        "name": "CSIA-PME",
        "url": "https://swiss-ai-center.ch/",
        "email": "info@swiss-ai-center.ch",
    },
    swagger_ui_parameters={
        "tagsSorter": "alpha",
        "operationsSorter": "method",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0 (GNU AGPLv3)",
        "url": "https://choosealicense.com/licenses/agpl-3.0/",
    },
)
...
```

1. Import the OpenCV library and the get_extension function from the tasks service. This function is used to guess the extension of the image based on the input type.
2. Change the description of the service.
3. Change the name and the slug of the service. This is used to identify the service in the engine.
4. Change the input/output fields of the service. The name of the field is the key of the dictionary that will be used in the process function. The type of the field is the type of the data that will be sent to the service. They are defined in the FieldDescriptionType enum.
5. Change the process function. This is the core of the service. The data is a dictionary with the keys being the field names set in the data_in_fields. The result must be a dictionary with the keys being the field names set in the data_out_fields.
6. Change the API description and summary.
7. Change the API title, version, contact and license.

##### 1.4.4 Dockerfile

The Dockerfile is used to build the Docker image of the service. We need to copy the model in the docker.

```dockerfile hl_lines="6"
# Copy model
# TODO: 1. Change the name of the model file to match the name of your model file
COPY ae_model.h5 .
```

1. Change the name of the model file to match the name of your model file.

#### 1.5 Create the Workflow for GitHub Actions

First, if you don't have the file already, download the `sample-service-without-model.yml` file from the [GitHub repository](https://github.com/csia-pme/services-templates/workflows) and rename it to `ano-detection.yml` in the `.github/workflows` folder.

Open it with your IDE and modify the `sample-service` texts with `ano-detection`

```yaml hl_lines="3-4 9 19 21 37 43 54 56 63 69 71 75-78 81 89 91-96"
# Documentation: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsuses
# TODO: 1. CHANGE THE NAME AND THE RUN NAME (1)!
name: ano-detection_workflow
run-name: ano-detection workflow

# Allow one concurrent deployment
concurrency:
  # TODO: 2. CHANGE THE GROUP NAME (2)!
  group: "ano-detection"
  cancel-in-progress: true

on:
  push:
    paths:
      - .github/actions/build-and-push-docker-image-to-github/action.yml
      - .github/actions/execute-command-on-kubernetes-cluster/action.yml
      - .github/actions/test-python-app/action.yml
      # TODO: 3. CHANGE THE WORKFLOW NAME (3)!
      - .github/workflows/ano-detection.yml
      # TODO: 4. CHANGE THE PATH TO THE PYTHON APP (4)!
      - services/ano-detection/**/*

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  run-workflow:
    runs-on: ubuntu-latest
    steps:
      - name: Clone repository
        uses: actions/checkout@v3

      - name: Lint Python app
        uses: ./.github/actions/lint-python-app
        with:
          # TODO: 5. CHANGE THE PATH TO THE PYTHON APP (5)!
          python-app-path: ./services/ano-detection

      - name: Test Python app
        uses: ./.github/actions/test-python-app
        with:
          # TODO: 6. CHANGE THE PATH TO THE PYTHON APP (6)!
          python-app-path: ./services/ano-detection

      - name: Build and push Docker image to GitHub
        id: build-and-push-docker-image-to-github
        # Only run on main
        if: github.ref == 'refs/heads/main'
        uses: ./.github/actions/build-and-push-docker-image-to-github
        with:
          docker-registry-username: ${{ github.actor }}
          docker-registry-password: ${{ secrets.GITHUB_TOKEN }}
          # TODO: 7. CHANGE THE DOCKER IMAGE NAME (7)!
          docker-image-name: ${{ github.repository }}-ano-detection
          # TODO: 8. CHANGE THE PATH TO THE DOCKER IMAGE CONTEXT (8)!
          docker-image-context: ./services/ano-detection

      - name: Prepare configuration files with secrets from GitHub Secrets
        # Only run on main
        if: github.ref == 'refs/heads/main'
        shell: bash
        # TODO: 9. CHANGE THE PATH TO THE KUBERNETES CONFIGURATION FILES (9)!
        working-directory: services/ano-detection/kubernetes
        env:
          ENVIRONMENT: production
          LOG_LEVEL: info
          ENGINE_URL: https://engine-csia-pme.kube.isc.heia-fr.ch
          # TODO: 10. CHANGE THE URL OF THE SAMPLE SERVICE (10)!
          SERVICE_URL: https://ano-detection-csia-pme.kube.isc.heia-fr.ch
        # TODO: 11. CHANGE THE NAME OF THE CONFIGURATION FILES (11)!
        run: |
          # Set ano-detection version
          docker_image_tags=(${{ steps.build-and-push-docker-image-to-github.outputs.docker-image-tags }})
          docker_image_sha_tag="${docker_image_tags[1]}"
          yq ".spec.template.spec.containers[0].image = \"$docker_image_sha_tag\"" ano-detection.stateful.yml > new-ano-detection.stateful.yml && mv new-ano-detection.stateful.yml ano-detection.stateful.yml

          # Set ano-detection configuration
          yq '.data = (.data | to_entries | map({"key": .key, "value": "${" + .key + "}"}) | from_entries)' ano-detection.config-map.yml | envsubst > new-ano-detection.config-map.yml && mv new-ano-detection.config-map.yml ano-detection.config-map.yml

      # TODO: 12. CHANGE THE NAME OF THE ACTION (12)!
      - name: Deploy ano-detection on the Kubernetes cluster
        # Only run on main
        if: github.ref == 'refs/heads/main'
        uses: ./.github/actions/execute-command-on-kubernetes-cluster
        with:
          kube-config: ${{ secrets.KUBE_CONFIG }}
          kube-namespace: csia-pme-prod
          # TODO: 13. CHANGE THE KUBERNETES CONTEXT (13)!
          kubectl-context: ./services/ano-detection/kubernetes
          # TODO: 14. CHANGE THE PATH TO THE KUBERNETES CONFIGURATION FILES (14)!
          kubectl-args: |
            apply \
              -f ano-detection.config-map.yml \
              -f ano-detection.stateful.yml \
              -f ano-detection.service.yml \
              -f ano-detection.ingress.yml
```

1. Change the name and the run name of the workflow.
2. Change the group name.
3. Change the workflow name.
4. Change the path to the Python app.
5. Change the path to the Python app.
6. Change the path to the Python app.
7. Change the Docker image name.
8. Change the path to the Docker image context.
9. Change the path to the Kubernetes configuration files.
10. Change the URL of the sample service.
11. Change the name of the configuration files.
12. Change the name of the action.
13. Change the Kubernetes context.
14. Change the path to the Kubernetes configuration files.

!!! info "Note"
    The host can be changed to your own domain name if the service is deployed on another Kubernetes cluster.

!!! success "Congratulations!"
    You have successfully created a service locally. Now, you can push the service to GitHub and deploy it on the engine using the workflow created in the previous section.