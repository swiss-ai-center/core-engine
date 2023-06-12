# Authorization and authentication

Authorization and authentication have been designed, but not implemented.

The [engine](./engine.md) is responsible for the authorization and authentication.

## Service authorization
Services may require a token to authenticate the engine. The engine will store the authentication token in it's database.
If the service is secured by `https`, the token may be directly stored in the service's `URL`. In any case, if the service isn't using `https`, the _secret_ token may not be _secret_.

## User authentication
Authentication will be delegated to a [OpenID](https://en.wikipedia.org/wiki/OpenID) compliant service, for instance
[SWITCH edu-ID](https://www.switch.ch/edu-id/), [keycloak](https://www.keycloak.org/), ...

```mermaid
sequenceDiagram
    actor User
    participant Auth service
    participant CSIA Engine

    Note over User, Auth service: The user request a token
    User->>Auth service: request token(credentials)
    Auth service->>User: Auth token

    Note over User, CSIA Engine: Given an auth token, the user can access the engine
    User->>CSIA Engine: Start service (Auth token + service parameters)
    CSIA Engine->>User: Start service (Auth token + service parameters)
```

## Authorization
A matrix of groups of users and a matrix of groups and authorizations will be used
to store the permissions, for each services.

## Identified key points
* When the engine is first started, an *admin* user must be created
* Service registration must be authorized. For instance an authorized user asks for a token that will be used to auhorize the service registration.
