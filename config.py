import boto3
import json
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()

class Settings(BaseSettings):
    BEDROCK_REGION: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    LLM_MODEL_ID: str
    IMAGE_GEN_MODEL_ID: str
    CDN_URL: str
    S3_BUCKET: str
    DYNAMODB_TABLE: str


def get_secrets():
    settings = Settings()

    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name="us-west-2"
        )
        get_secret_value_response = client.get_secret_value(
            SecretId="image-gen"
        )

        secrets = json.loads(get_secret_value_response['SecretString'])
        settings.BEDROCK_REGION = secrets.get('BEDROCK_REGION')
        settings.AWS_ACCESS_KEY = secrets.get('AWS_ACCESS_KEY')
        settings.AWS_SECRET_KEY = secrets.get('AWS_SECRET_KEY')
        settings.LLM_MODEL_ID = secrets.get('LLM_MODEL_ID')
        settings.IMAGE_GEN_MODEL_ID = secrets.get('IMAGE_GEN_MODEL_ID')
        settings.CDN_URL = secrets.get('CDN_URL')
        settings.S3_BUCKET = secrets.get('S3_BUCKET')
        settings.DYNAMODB_TABLE = secrets.get('DYNAMODB_TABLE')
    except Exception as e:
        return dict()
    
    return settings


config = get_secrets()
