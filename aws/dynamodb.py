import boto3
import json
from decimal import Decimal
from config import config


class DynamoDB:
    def __init__(self, table_name):
        self.db = boto3.resource('dynamodb',
                                region_name=config.BEDROCK_REGION,
                                aws_access_key_id=config.AWS_ACCESS_KEY,
                                aws_secret_access_key=config.AWS_SECRET_KEY,
                            )
        self.name = table_name
        self.table = self.db.Table(table_name)
        
    def get_item(self, key):
        response = self.table.get_item(Key={
            'id': key
        })
        return json.loads(json.dumps(response.get('Item'), default=_decimal_default))
    
    
    def put_item(self, item: dict):
        self.table.put_item(
            Item=json.loads(json.dumps(item), parse_float=Decimal)
        )

    def delete_item(self, id):
        self.table.delete_item(Key={"id": id})
        
    def scan_items(self, query):
        return self.table.scan(**query)


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
