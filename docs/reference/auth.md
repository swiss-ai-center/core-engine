# Authorization and authentication

Authorization and authentication have been designed, but not implemented.

The [core-engine](./core-engine.md) is responsible for the authorization and authentication.

## Service authorization

<<<<<<< HEAD
Services may require a token to authenticate the engine. The engine will store the authentication token in its database.
=======
Services may require a token to authenticate the core-engine. The core-engine will store the authentication token in it's database.
>>>>>>> 9a35681 (Rename engine to core-engine)
If the service is secured by `https`, the token may be directly stored in the service's `URL`. In any case, if the service isn't using `https`, the _secret_ token may not be _secret_.

## User authentication

Authentication will be delegated to a [OpenID](https://en.wikipedia.org/wiki/OpenID) compliant service, for instance
[SWITCH edu-ID](https://www.switch.ch/edu-id/), [keycloak](https://www.keycloak.org/), ...

```mermaid
sequenceDiagram
    actor User
    participant Auth service
<<<<<<< HEAD
    participant Core Engine
=======
    participant CSIA Core Engine
>>>>>>> 9a35681 (Rename engine to core-engine)

    Note over User, Auth service: The user request a token
    User->>Auth service: request token(credentials)
    Auth service->>User: Auth token

<<<<<<< HEAD
    Note over User, Core Engine: Given an auth token, the user can access the engine
    User->>Core Engine: Start service (Auth token + service parameters)
    Core Engine->>User: Start service (Auth token + service parameters)
=======
    Note over User, CSIA Engine: Given an auth token, the user can access the core-engine
    User->>CSIA Engine: Start service (Auth token + service parameters)
    CSIA Engine->>User: Start service (Auth token + service parameters)
>>>>>>> 9a35681 (Rename engine to core-engine)
```

## Authorization

A matrix of groups of users and a matrix of groups and authorizations will be used
to store the permissions, for each service.

## Identified key points

* When the core-engine is first started, an _admin_ user must be created
* Service registration must be authorized. For instance an authorized user asks for a token that will be used to authorize the service registration.
