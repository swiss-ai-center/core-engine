# How to add DVC to a service

This guide will help you add DVC to your service.

## Guide

### Install DVC

<https://dvc.org/doc/install>

You can install DVC with `pip`, but make sure to install with s3 optional dependencies.

```sh
pip install dvc[s3]
```

### Initialize DVC

<https://dvc.org/doc/command-reference/init>

Now that DVC is installed we have to init it, so go to your service folder and use this command.

```sh
dvc init --subdir
```

The `--subdir` is important because we are in a monorepos

### Create a bucket on Minio

Go to your MinIO server, connect with the provided credentials and use the GUI to create your bucket.

### Configure DVC for Minio

<https://dvc.org/doc/command-reference/remote/add>

```sh
dvc remote add -d myremote s3://name-of-your-bucket

dvc remote modify myremote endpointurl https://<SERVER_ADDRESS>:<PORT>
```

To configure your credentials for DVC do not use the `dvc remote modify` instead install AWS CLI.

```sh
pip install awscli
```

Use aws configure to add your Access Key ID and your Secret Access Key.

```sh
aws configure
```

### Add your dataset

Modify the path for your dataset

```sh
dvc add path/data.csv
```

Push to DVC

```sh
dvc push
```

## Related explanations

These explanations are related to the current item (in alphabetical order).

- [About DVC](../explanations/about-dvc.md)

## Resources

These resources are related to the current item (in alphabetical order).

_None at the moment._
