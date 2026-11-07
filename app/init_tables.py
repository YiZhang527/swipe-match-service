"""Create tables if missing. Used by local docker compose and tests (not on AWS, where Terraform creates them)."""
import time

from botocore.exceptions import BotoCoreError

from app import db


def table_specs():
    return [
        {
            "TableName": db._swipes_table_name(),
            "KeySchema": [
                {"AttributeName": "swiper_id", "KeyType": "HASH"},
                {"AttributeName": "swipee_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "swiper_id", "AttributeType": "S"},
                {"AttributeName": "swipee_id", "AttributeType": "S"},
            ],
            "BillingMode": "PAY_PER_REQUEST",
        },
        {
            "TableName": db._matches_table_name(),
            "KeySchema": [
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "match_user_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "match_user_id", "AttributeType": "S"},
            ],
            "BillingMode": "PAY_PER_REQUEST",
        },
    ]


def create_tables():
    client = db._client()
    existing = client.list_tables()["TableNames"]
    for spec in table_specs():
        if spec["TableName"] not in existing:
            client.create_table(**spec)


if __name__ == "__main__":
    # DynamoDB Local may take a few seconds to start
    for _ in range(30):
        try:
            create_tables()
            print("Tables ready")
            break
        except BotoCoreError:
            time.sleep(1)
    else:
        raise SystemExit("DynamoDB not reachable")
