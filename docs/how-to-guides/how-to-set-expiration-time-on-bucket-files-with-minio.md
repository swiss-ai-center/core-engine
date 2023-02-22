# How to set expiration time on bucket files with MinIO

This guide will help you setting an expiration time on a MinIO bucket. This will allow to automatically delete files after a certain time.

## Guide

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

## Related explanations

These explanations are related to the current item (in alphabetical order).

- [About MinIO](../explanations/about-minio.md)

## Resources

These resources are related to the current item (in alphabetical order).

- [MinIO Object Lifecycle Management](https://min.io/docs/minio/linux/administration/object-management/object-lifecycle-management.html)
