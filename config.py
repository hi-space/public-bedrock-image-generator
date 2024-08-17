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

config = Settings()
