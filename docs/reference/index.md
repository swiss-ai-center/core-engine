# Reference

## Engine and Webapp

| Service                                           | Code                                                      | URL when run locally with minikube    | URL when deployed on Fribourg's Kubernetes            |
| ------------------------------------------------- | --------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------- |
| [Engine](./engine.md){ style="color: inherit;" }  | <https://github.com/csia-pme/csia-pme/tree/main/engine>   | <http://localhost:8080/docs>          | <https://engine-csia-pme.kube.isc.heia-fr.ch/docs>    |
| [Webapp](./webapp.md){ style="color: inherit;" }  | <https://github.com/csia-pme/csia-pme/tree/main/webapp>   | <http://localhost:8181/docs>          | <https://webapp-csia-pme.kube.isc.heia-fr.ch/docs>    |

## Services

| Service                                                                   | Code                                                                          | URL when run locally with minikube    | URL when deployed on Fribourg's Kubernetes                    |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------- |
| [ae_ano_detection](./ae-ano-detection.md){ style="color: inherit;" }      | <https://github.com/csia-pme/csia-pme/tree/main/services/ae_ano_detection>    | <http://localhost:8282/docs>          | <https://ae-ano-detection-csia-pme.kube.isc.heia-fr.ch/docs>  |
| [average_shade](./average-shade.md){ style="color: inherit;" }            | <https://github.com/csia-pme/csia-pme/tree/main/services/average_shade>       | <http://localhost:8383/docs>          | <https://average-shade-csia-pme.kube.isc.heia-fr.ch/docs>     |
| [digit_recognition](./digit-recognition.md){ style="color: inherit;" }    | <https://github.com/csia-pme/csia-pme/tree/main/services/digit_recognition>   | <http://localhost:8484/docs>          | <https://digit-recognition-csia-pme.kube.isc.heia-fr.ch/docs> |
| [face_analyzer](./face-analyzer.md){ style="color: inherit;" }            | <https://github.com/csia-pme/csia-pme/tree/main/services/face_analyzer>       | <http://localhost:8585/docs>          | <https://face-analyzer-csia-pme.kube.isc.heia-fr.ch/docs>     |
| [face_detection](./face-detection.md){ style="color: inherit;" }          | <https://github.com/csia-pme/csia-pme/tree/main/services/face_detection>      | <http://localhost:8686/docs>          | <https://face-detection-csia-pme.kube.isc.heia-fr.ch/docs>    |

This sequence diagram illustrates the interaction between an user and the service, without using the Engine.

```mermaid
sequenceDiagram
    participant S as s - Service
    participant C as c - Client
    participant S3 as s3 - Storage
    C->>+S3: file_keys = for file in data: upload(file)
    S3-->>-C: return(200, file_key)
    C->>+S: POST(s.url, callback_url: str, service_task: ServiceTask)
    Note right of S: callback_url is the url where the service should send the response
    Note right of S: service_task should match the model
    S-->>-C: return(200, Task added to the queue)
    S->>+S3: data = for key in service_task.task.data_in: get_file(service_task.s3_infos, key)
    S3-->>-S: return(200, stream)
    S->>S: result = process(data)
    S->>+S3: data_out = for res in result: upload_file(service_task.s3_infos, data_out)
    S3-->>-S: return(200, key)
    S->>S: task_update = jsonable_encoder(TaskUpdate({status: finished, task.data_out: data_out}))
    S->>+C: PATCH(callback_url, task_update)
    C-->>-S: return(200, OK)
    C->>+S3: GET(task_update.data_out)
    S3-->>-C: return(200, stream)
```
