# Description
Simple S3 client written in python that allows to push or pull data from/to a S3 bucket. This script was built and tested with python 3.9.

# How to run
## Usage
The script will use the following environment variables in order to connect to S3:

- S3_URL: url to the S3 storage server, only applicable for a "S3" storage type
- S3_ZONE: zone of the S3 storage server, only applicable for a "S3" storage type
- S3_KEY_ID: key to connect to the S3 storage server, only applicable for a "S3" storage type
- S3_SECRET_KEY: secret to connect to the S3 storage server, only applicable for a "S3" storage type

Then, the CLI arguments are:

```bash
python3 s3client.py [push/pull] path/to/local/file bucket/somedir/someFile
```

## Install dependencies
First, install dependencies:

```bash
pip3 install -r requirements.txt
```

## Run
Then, run with:
```bash
S3_URL="https://S3SERVERURL:PORT" S3_KEY_ID="THEKEYID" S3_SECRET_KEY="THESECRETKEY" python s3client.py push path/to/local/file bucket/somedir/someFile
```
