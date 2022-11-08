# Create a GitHub Secrets

These steps allow to create/update a secret stored on [GitHub Secrets](../tools/github-secrets.md).

## Guide

Access [GitHub Actions Secrets](https://github.com/csia-pme/csia-pme/settings/secrets/actions) page to have an overview of the available secrets.

Add a secret by selecting **New repository secret**.

**Note**: A secret can only be updated, not viewed. Please be careful to have a copy of the secrets you store on GitHub Secrets.

The secrets have the following structure:

`<APPLICATION>_<SERVICE>_<NAME OF THE ENVIRONMENT VARIABLE>`

For example, the [Engine](../engine/readme.md) application has three services: [MinIO](../tools/minio.md), [Mongo](../tools/mongo.md) and the Engine. The environment variables are then formatted as follow:

- `ENGINE_MINIO_[...]`
- `ENGINE_MONGO_[...]`
- `ENGINE_ENGINE_[...]`

## Related items

These items are related to the the current item (in alphabetical order).

- [Install and configure the virtual machine](./install-and-configure-the-virtual-machine.md)
