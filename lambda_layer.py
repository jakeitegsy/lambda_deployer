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
			return (
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

	def delete_previous_layer_version(self):
		for version in self.get_layer_version():
			self.lambda_client.delete_layer_version(
				LayerName=self.name, VersionNumber=version
			)
			print(f'Layer Version: {version} deleted in {self.environment_name}')
