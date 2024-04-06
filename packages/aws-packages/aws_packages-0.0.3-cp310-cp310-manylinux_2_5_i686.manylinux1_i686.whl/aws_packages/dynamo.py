import boto3
from boto3.dynamodb.conditions import Key

_dynamodb_client = boto3.resource("dynamodb")


def get_dynamodb_client():
    return _dynamodb_client


class DataHandler:
    def __init__(self, table_name, logger, client=None, key="pk"):
        self.key = key
        if client is None:
            self._client = get_dynamodb_client()
        else:
            self._client = client
        self._table_name = table_name
        self._logger = logger
        self.table = self._client.Table(self._table_name)

    def add_item(self, identifier, value):
        self.table.put_item(Item={self.key: identifier, **value})

    def get_item(self, identifier):
        response = self.table.query(KeyConditionExpression=Key(self.key).eq(identifier))
        items = response["Items"]

        if not items:
            return None

        if len(items) > 1:
            raise Exception(f"More than one item found for {identifier}")

        print(items)

        entry = items[0]
        return entry
