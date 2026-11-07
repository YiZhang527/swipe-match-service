import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def _region():
    return os.getenv("AWS_REGION", "us-east-1")


def _swipes_table_name():
    return os.getenv("SWIPES_TABLE", "swipes")


def _matches_table_name():
    return os.getenv("MATCHES_TABLE", "matches")


def _endpoint():
    # Set only for local DynamoDB (docker compose); unset on AWS
    return os.getenv("DYNAMODB_ENDPOINT") or None


def _resource():
    return boto3.resource("dynamodb", region_name=_region(), endpoint_url=_endpoint())


def _client():
    return boto3.client("dynamodb", region_name=_region(), endpoint_url=_endpoint())


def put_swipe(swiper_id, swipee_id, direction, now):
    # Re-swiping overwrites the previous decision
    _resource().Table(_swipes_table_name()).put_item(
        Item={
            "swiper_id": swiper_id,
            "swipee_id": swipee_id,
            "direction": direction,
            "swiped_at": now,
        }
    )


def has_right_swiped(swiper_id, swipee_id):
    resp = _resource().Table(_swipes_table_name()).get_item(
        Key={"swiper_id": swiper_id, "swipee_id": swipee_id},
        ConsistentRead=True,
    )
    item = resp.get("Item")
    return item is not None and item["direction"] == "right"


def create_match(user_a, user_b, now):
    """Write one item per user so each side can query by partition key.
    Returns True if a new match was created, False if it already existed."""
    table = _matches_table_name()

    def put(u, v):
        return {
            "Put": {
                "TableName": table,
                "Item": {
                    "user_id": {"S": u},
                    "match_user_id": {"S": v},
                    "matched_at": {"S": now},
                },
                "ConditionExpression": "attribute_not_exists(user_id)",
            }
        }

    try:
        _client().transact_write_items(TransactItems=[put(user_a, user_b), put(user_b, user_a)])
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "TransactionCanceledException":
            return False
        raise


def get_matches(user_id):
    table = _resource().Table(_matches_table_name())
    kwargs = {"KeyConditionExpression": Key("user_id").eq(user_id)}
    items = []
    while True:
        resp = table.query(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            return items
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
