# About MinIO

As the website of [MinIO](https://min.io/) mentions:

!!! quote

    MinIO offers high-performance, S3 compatible object storage.

## How and why do we use MinIO

We use MinIO to store our datasets and models from DVC.

## Install MinIO

TODO

## Configuration

_None._

## Common tasks

### Create a bucket on Minio

Go to your MinIO server, connect with the provided credentials and use the GUI to create your bucket.

### Configure the bucket to delete files after a certain time

Select your bucket and go to **Lifecycle**.

Add a lifecycle rule by clicking **Add Lifecycle Rule**.

Configure the new lifecycle rule as follow:

- **Type of lifecycle**: Expiry
- **After**: The number of days after which the files older than this will be deleted

Click **Save** to save the lifecycle rule.

All files older than the specified number of days will be automatically deleted.

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

- [MinIO Object Lifecycle Management](https://min.io/docs/minio/linux/administration/object-management/object-lifecycle-management.html)
