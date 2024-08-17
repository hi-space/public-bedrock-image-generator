import boto3
from config import config


class S3:
    def __init__(self, bucket_name):
        self.storage = boto3.client('s3',                            
            region_name = config.BEDROCK_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
        )
        self.bucket_name = bucket_name

    def upload_object(self, bytes, key, extra_args={}):
        self.storage.upload_fileobj(
            bytes,
            self.bucket_name,
            key,
            ExtraArgs=extra_args
        )

    def get_object(self, key):
        self.storage.get_object(Bucket=self.bucket_name, Key=key)
