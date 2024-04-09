########################################################################################################################
# IMPORTS

import io
import logging

import boto3

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class AWSInterface:

    def __init__(self, config):
        if 'aws' in config:
            self.config = config['aws']

            self.profile = self.config['profile']
            self.bucket = self.config['bucket']

            self.session = boto3.Session(profile_name=self.profile)

            self.s3 = self.session.resource('s3')
            self.s3_client = self.s3.meta.client

        else:
            logger.warning('no aws section in config')

    def get_file(self, s3_path):
        try:
            return self.s3.Object(self.bucket, s3_path).get()
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f'{s3_path} does not exist')

    def read_file_as_bytes(self, s3_path):
        return io.BytesIO(self.get_file(s3_path)['Body'].read())

    def upload_file(self, local_path, s3_path):
        self.s3.Bucket(self.bucket).upload_file(local_path, s3_path)
        
