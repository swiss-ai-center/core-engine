# Service

This page describes the service architecture and its specifications.

The service is a [FastAPI](https://fastapi.tiangolo.com/) application that is deployed on a Kubernetes cluster. It is a REST API that can be used to process data.

## Architecture

To see the general architecture of the project, see the global [UML Diagram](../reference/core-engine.md#uml-diagram).

This sequence diagram illustrates the interaction between an user and a service, without using the Core Engine.

```mermaid
sequenceDiagram
    participant S as s - Service
    participant C as c - Client
    participant S3 as s3 - Storage
    C->>+S3: file_keys = for file in data: upload(file)
    S3-->>-C: return(200, file_key)
    C->>+S: POST(s.url/process, callback_url: str, service_task: ServiceTask)
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

## Specifications

Inside the project, the services are implemented using Python. But the service is a REST API, so it can be implemented in any language.

### Endpoints

To match the specifications, the service must implement the following endpoints:

- GET `/status` : returns the service availability. (Returns a string)
- GET `/tasks/{task_id}/status` : returns the status of a task. (Returns a string)
- POST `/compute` : computes the given task and returns the result. (Returns a string)

![service-endpoints](../assets/screenshots/service-endpoints.png)

### Models

The different models used in the pipeline are described below.

#### Task Input

The `POST /compute` endpoint must be able to receive a JSON body that matches the following model:

```python
class ServiceTaskTask(BaseModel):
    """
    Task update model
    This model is used to update a task
    """
    id: UUID
    data_in: List[str]
    service_id: UUID
    pipeline_id: UUID | None


class ServiceTaskBase(BaseModel):
    """
    Base class for Service task
    This model is used in subclasses
    """
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str
    s3_host: str
    s3_bucket: str
    task: ServiceTaskTask
    callback_url: str
```

The `data_in` and `data_out` fields are lists of S3 object keys. The `status` field is a string that can be one of the following values:

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    PROCESSING = "processing"
    SAVING = "saving"
    FINISHED = "finished"
    ERROR = "error"
    UNAVAILABLE = "unavailable"
```

The S3 settings are used to connect to the S3 storage where the data is stored and where the result will be stored. The `callback_url` is the url where the service should send the response.

A JSON representation would look like this:

```json
{
  "s3_access_key_id": "access_key",
  "s3_secret_access_key": "secret_key",
  "s3_region": "eu-west-3",
  "s3_host": "test.s3.com",
  "s3_bucket": "test-bucket",
  "task": {
    "data_in": [
      "key1-in.png",
      "key2-in.json"
    ],
    "service_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "pipeline_id": "45a85f64-5717-4562-b3fc-34a6f66afa6",
    "id": "76ba4e6a-3b8a-4bda-8407-6eaf5a8e1100"
  },
  "callback_url": "http://my-url.com/callback"
}
```

#### Task Output

Once the task is computed, the service must PATCH the task on `/tasks/{task_id}` with the following model:

```python
class TaskUpdate(BaseModel):
    """
    Task update model
    This model is used to update a task
    """
    service: str | None
    url: str | None
    data_out: List[str] | None
    status: TaskStatus | None
```

The `data_out` field is a list of S3 object keys. The `status` field is a string that can be one of the following values:

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    PROCESSING = "processing"
    SAVING = "saving"
    FINISHED = "finished"
    ERROR = "error"
    SCHEDULED = "scheduled"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"
```

A JSON representation would look like this:

```json
{
  "service": "service-name",
  "url": "http://service-url",
  "data_out": [
    "key1-out.png",
  ],
  "status": "finished"
}
```

### Register to the Core Engine

To register the service to the Core Engine, the service must send a POST request to the Core Engine `/services` endpoint with the following model:

```python
class ExecutionUnitBase(CoreModel):
    """
    ExecutionUnit model
    """
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    summary: str = Field(nullable=False)
    description: str | None = Field(default=None, nullable=True)
    status: ExecutionUnitStatus = Field(default=ExecutionUnitStatus.AVAILABLE, nullable=False)
    data_in_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    data_out_fields: List[FieldDescription] | None = Field(sa_column=Column(JSON), default=None, nullable=True)
    tags: List[ExecutionUnitTag] | None = Field(sa_column=Column(JSON), default=None, nullable=True)

    # Needed for Column(JSON) to work
    class Config:
        arbitrary_types_allowed = True

class ExecutionUnitStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


class ServiceBase(ExecutionUnitBase):
    """
    Base class for a Service
    This model is used in subclasses
    """
    url: AnyHttpUrl = Field(nullable=False)
```

The `data_in_fields` and `data_out_fields` fields are lists of `FieldDescription` models. A `FieldDescription` model is defined as follows:

```python
class FieldDescriptionType(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"
    AUDIO_MP3 = "audio/mpeg"
    AUDIO_OGG = "audio/ogg"


class FieldDescription(TypedDict):
    """
    Field description
    """
    name: str
    type: List[FieldDescriptionType]
```

The `url` field is the url of the service.

A JSON representation would look like this:

```json
{
  "name": "service-name",
  "slug": "service-slug",
  "url": "http://service-url",
  "summary": "service-summary",
  "description": "service-description",
  "status": "available",
  "data_in_fields": [
    {
      "name": "image",
      "type": [
        "image/jpeg",
        "image/png"
      ]
    },
    {
      "name": "text",
      "type": [
        "text/plain"
      ]
    }
  ],
  "data_out_fields": [
    {
      "name": "image",
      "type": [
        "image/jpeg",
        "image/png"
      ]
    }
  ],
  "tags": [
    {
      "name": "Neural Networks",
      "acronym": "NN"
    }
  ]
}
```

After the service is registered, it will be available on the Core Engine's `/service-slug` endpoint.
