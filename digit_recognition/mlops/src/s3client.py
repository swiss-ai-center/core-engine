import os
import asyncio
import aioboto3
import argparse

async def main():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument("action", choices=["push", "pull"])
	parser.add_argument("local")
	parser.add_argument("remote")
	args = parser.parse_args()

	path = args.remote.split("/")
	if len(path) < 2:
		print("Remote identifier must be: bucket/some/id") # noqa
		return

	bucketName = path[0]
	remoteId = str.join("/", path[1:])

	s3_url = os.environ["S3_URL"] if "S3_URL" in os.environ else None
	s3_zone = os.environ["S3_ZONE"] if "S3_ZONE" in os.environ else None
	s3_key = os.environ["S3_KEY_ID"] if "S3_KEY_ID" in os.environ else None
	s3_secret = os.environ["S3_SECRET_KEY"] if "S3_SECRET_KEY" in os.environ else None

	session = aioboto3.Session()
	async with session.resource("s3", endpoint_url=s3_url, region_name=s3_zone, aws_secret_access_key=s3_secret, aws_access_key_id=s3_key) as s3:
		bucket = None
		async for b in s3.buckets.all():
			if b.name == bucketName:
				bucket = b
				break
		if bucket is None:
			print("Creating bucket", bucketName) # noqa
			bucket = await s3.create_bucket(Bucket=bucketName)

		if args.action == "push":
			f = open(args.local, "rb")
			await bucket.put_object(Key=remoteId, Body=f)
			f.close()
		elif args.action == "pull":
			await bucket.download_file(Key=remoteId, Filename=args.local)

asyncio.run(main())

