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
