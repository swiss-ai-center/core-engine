# Description
The goal of this project is to trigger the pipeline to create the dataset we want to train the new model and to provide it for the other service through the S3 server. To trigger the pipeline, simply edit the `numbers.dat` file with the list of the numbers which the model should recognize.

# Use Case
1. Edit the `numbers.dat` file with the numbers wanted -> Format
2. commit changes (the rest is done by the ci pipeline)

# Format
The file `numbers.dat` should contain the list of the numbers respecting the following syntaxe :
- Ascending order of the numbers
- Numbers between 0 and 9 included
- Numbers splitted by `,` character

# Artifacts
## Dataset Generation
The datasets are pushed with DVC on the S3 and create the DVC files, which are kept as jobs artifacts. They let us track the dataset on the S3 remote server.

## Model Generation
The model is pushed on the S3 with a predifined name based on the numbers it can recognize. The training generated graphs to track its performances, which are kept as artifacts. The console also output the accuracy compared to the raw testset and the name of the model pushed on the S3.

# Scripts
This scripts are automatically triggered by the gitlab-ci pipeline.

## Automation
- `script_create_dataset` : Get digits from numbers.dat file and parse the list of numbers to pass it as arguments to `create_other_model.py`
- `script_push_model` : Get digits from numbers.dat file and specify the correct name to push the model on the S3
## ML
- `create_default_model` : Create the pre-trained model from the complet MNIST dataset (recognize numbers from 0 to 9)
- `generate_mnist_sub_dataset` : Generate a sub dataset from the default dataset by precising which digits to keep. The test dataset will contain all the digits like the default one (to compare between different sub dataset)
- `create_other_model` : Create a pretrained model based on `train.csv` and `test.csv`
- `s3client` : Manage the connection to the remote Minio S3 server
