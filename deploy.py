from argparse import ArgumentParser
from lambda_function import LambdaFunction
from lambda_layer import LambdaLayer

def main():
	parser = ArgumentParser(description='Update Existing Lambda Functions or Publish Layers')
	parser.add_argument("-f", "--deploy_function", help='Package and Deploy a Lambda Function to S3. Update the Lambda Function if it exists, requires bucket_name')
	parser.add_argument("-l", "--publish_layer", nargs="+", help='Package and Publish Lambda Layer(s) requires bucket_name')
	parser.add_argument("-g", "--package_layer", nargs="+", help='Package Lambda Layer(s)')
	parser.add_argument("-b", "--bucket_name", required=False)
	parser.add_argument("-p", "--profile_name", required=False)

	args = parser.parse_args()

	if args.deploy_function:
		print(f'Creating Package for {args.deploy_function}')
		LambdaFunction(
			args.deploy_function,
			bucket_name=args.bucket_name, profile_name=args.profile_name
		)

	if args.package_layer:
		print(f'Creating Lambda Layer Package for dependencies: {", ".join(args.package_layer)}...')
		lambda_layer = LambdaLayer(args.package_layer)


	if args.publish_layer:
		print(f'Packaging and Publishing Lambda Layer for dependencies: {", ".join(args.publish_layer)}...')
		lambda_layer = LambdaLayer(args.publish_layer, bucket_name=args.bucket_name, profile_name=args.profile_name)
		lambda_layer.upload_to_s3()
		lambda_layer.delete_previous_layer_version()
		lambda_layer.publish_layer()
		lambda_layer.delimiter()
		lambda_layer.delete_directory()
		lambda_layer.delete_zipfile()


if __name__ == '__main__':
	main()