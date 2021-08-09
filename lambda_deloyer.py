import boto3 

from argparse import ArgumentParser
from os import environ, system, chdir, remove
from shutil import rmtree, make_archive
from zipfile import ZipFile

class LambdaDeployer:

	def __init__(self, profile_name=None, bucket_name=None, region='us-west-2'):
		self.environment_name = profile_name
		self.s3_bucket = bucket_name
		self.region = region
		self.session = boto3.session.Session(
			region_name=self.region,
			profile_name=profile_name
		)
		self.s3 = self.session.client('s3')
		self.lambda_client = self.session.client('lambda')

	def delimiter(self):
		print("="*100)

	def s3_key(self):
		return f'{self.directory()}/{self.zip_filename()}'

	def upload_to_s3(self):
		self.delimiter()
		print(f"Uploading {self.zip_filename()} to S3://{self.s3_bucket}/{self.directory}...")

	def delete_directory(self):
		return rmtree(self.directory(), ignore_errors=True)

	def delete_zipfile(self):
		return remove(self.zip_filename())


class LambdaLayer(LambdaDeployer):

	def __init__(self, dependencies, bucket_name=None, profile_name='DEV', name=None):
		super().__init__(bucket_name=bucket_name, profile_name=profile_name)
		self.dependencies = dependencies
		self.set_name(name)
		self.delete_directory()
		self.package_layer()
		self.upload_to_s3()
		self.delete_previous_layer_version()
		self.publish_layer()
		self.delimiter()
		self.delete_directory()
		self.delete_zipfile()

	def set_name(self, name):
		try:
			self.name = self.dependencies[0] if name is None else name
		except IndexError:
			self.name = self.directory()

	def publish_layer(self):
		self.delimiter()
		message = f'Publishing {self.name} Layer::'
		try:
			self.lambda_client.publish_layer_version(
				LayerName=self.name,
				CompatibleRuntimes=['python3.6', 'python3.7', 'python3.8'],
				Content={
					'S3Bucket':  self.s3_bucket,
					'S3Key': self.s3_key,
				}
			)
		except (
			self.lambda_client.excpetions.ServiceExceptions,
			self.lambda_client.excpetions.ResourceNotFoundException,
			self.lambda_client.excpetions.TooManyRequestsException,
			self.lambda_client.excpetions.InvalidParameterValueException,
			self.lambda_client.excpetions.CodeStorageExceededException
		) as error:
			print(f'{message}FAILED::{error}')
		else:
			print(f'{message}Success')

	def directory(self):
		return 'lambda_layer'

	def runtime(self):
		return 'python'

	def package_layer(self):
		self.delimiter()
		print(f'Creating Archive for {self.name} Layer')
		system('python -m pip install -U pip')
		for dependency in self.dependencies:
			system(f'pip install --target ./{self.directory}/{self.runtime()}{dependency} --upgrade')
		make_archive(self.name, 'zip', root_dir=self.directory(), base_dir=self.runtime())

	def zip_filename(self):
		return f'{self.name}.zip'

	def s3_key(self):
		return f'{self.directory()}/{self.zip_filename()}'

	def get_layer_version(self):
		try:
			return(
				layer['Version']
				for layer in self.lambda_client.list_layer_versions(
					LayerName=self.name
				)['LayerVersions']
			)
		except (
			self.lambda_client.excpetions.ServiceExceptions,
			self.lambda_client.excpetions.ResourceNotFoundException,
			self.lambda_client.excpetions.TooManyRequestsException,
			self.lambda_client.excpetions.InvalidParameterValueException,
			KeyError,
		) as error:
			print(f'{message}FAILED::{error}')
		else:
			print(f'{message}Success')

	def delete_previous_layer_version(self):
		for version in self.get_layer_version():
			self.lambda_client.delete_layer_version(
				LayerName=self.name, VersionNumber=version
			)
			print(f'Layer Version: {version} deleted in {self.environment_name}')


class LambdaFunction(LambdaDeployer):

	def __init__(self, function_name, bucket_name=None, profile_name=None):
		super().__init__(bucket_name=bucket_name, profile_name=profile_name)
		self.function_name = function_name
		self.package_code()
		self.upload_to_s3()
		self.update_lambda_code()
		self.delimiter()
		self.delete_zipfile()

	def directory(self):
		return 'lambdas'

	def zip_filename(self):
		return f'{self.function_name}.zip'

	def python_filename(self):
		return f'{self.function_name}.zip'

	def package_code(self):
		self.delimiter()
		print(f'Zipping up {self.function_name} ...')
		make_archive(self.function, 'zip', root_dir=self.function_name)

	def update_lambda_code(self):
		self.delimiter()
		message = f'Updating {self.function_name} Lambda code in {self.environment_name}::'
		try:
			self.lambda_client.update_function_code(
				FunctionName=self.function_name,
				S3_Bucket=self.s3_bucket,
				S3Key=self.s3_key(),
				Publish=True,
			)
		except self.lambda_client.excpetions.ClientError as error:
			print(f'{message} FAILED::{error}')
		else:
			print(f'{message}Success')

def main():
	parser = ArgumentParser(description='Update Existing Lambda Functions or Publish Layers')
	parser.add_argument("-f", "--deploy_function", help='Package and Deploy a Lambda Function to S3. Update the Lambda Function if it exists')
	parser.add_argument("-l", "--publish_layer", nargs="+", help='Package and Publish Lambda Layer(s)')
	parser.add_arguument("-b", "--bucket_name", required=True)
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