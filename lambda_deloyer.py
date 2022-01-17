import boto3

from os import remove
from shutil import rmtree


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
		print(f"Uploading {self.zip_filename()} to s3://{self.s3_bucket}/{self.directory}...")

	def delete_directory(self):
		return rmtree(self.directory(), ignore_errors=True)

	def delete_zipfile(self):
		return remove(self.zip_filename())
