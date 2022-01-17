from argparse import ArgumentParser
from lambda_function import LambdaFunction
from lambda_layer import LambdaLayer

def main():
	parser = ArgumentParser(description='Update Existing Lambda Functions or Publish Layers')
	parser.add_argument("-f", "--deploy_function", help='Package and Deploy a Lambda Function to S3. Update the Lambda Function if it exists')
	parser.add_argument("-l", "--publish_layer", nargs="+", help='Package and Publish Lambda Layer(s)')
	parser.add_argument("-b", "--bucket_name", required=True)
	parser.add_argument("-p", "--profile_name")

	args = parser.parse_args()

	if args.deploy_function:
		print(f'Creating Package for {args.deploy_function}')
		LambdaFunction(
			args.deploy_function,
			bucket_name=args.bucket_name, profile_name=args.profile_name
		)

	if args.publish_layer:
		print(f'Creating Lambda Layer for dependencies: {", ".join(args.publish_layer)}')
		LambdaLayer(args.publish_layer, bucket_name=args.bucket_name, profile_name=args.profile_name)

if __name__ == '__main__':
	main()