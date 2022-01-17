# lambda_deployer

- Packages and Deploys AWS Lambda Functions and Layers
- Updates Lambda Functions it exists
- Downloads Layer dependencies, package and deploy Layer
- Updates Layer when it exists

## usage

### How to Deploy/Update a Lambda Function using a profile from the AWS CLI

```
$ python deploy.py --deploy_function lambda_function.py --bucket_name my-s3-bucket --profile_name TST
```

### How to Package and Deploy a Lambda Layer

This will download dependencies from PyPI and package them into a zip file

```
$ python deploy.py --publish_layer layer_name1,layer_nameN --bucket_name my-s3-bucket --profile_name PRD
```
