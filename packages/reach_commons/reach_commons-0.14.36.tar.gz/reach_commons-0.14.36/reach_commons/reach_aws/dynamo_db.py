import json
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from reach_commons.utils import DecimalEncoder, build_update_params_for_attributes


# noinspection PyMethodMayBeStatic
class BaseDynamoDBClient:
    def __init__(
        self,
        region_name="us-east-1",
        profile_name=None,
    ):
        self.region_name = region_name
        self.profile_name = profile_name


class DynamoDBClient(BaseDynamoDBClient):
    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )
        return session.client("dynamodb")

    def put_item(self, table_name, item):
        return self.client.put_item(TableName=table_name, Item=item)


class BusinessReviewsCommonQueries:
    @staticmethod
    def get_review_business_info(table, business_id: str) -> Dict:
        query_params = {
            "KeyConditionExpression": Key("PK").eq(f"business#{business_id}")
            & Key("SK").eq("info")
        }

        response = table.query(**query_params)

        if response["Items"]:
            business_info = response["Items"][0]
            return business_info
        else:
            return {}

    @staticmethod
    def patch_business_info(
        table,
        business_id: str,
        business_info: Dict,
        created_at_isoformat: str = None,
    ) -> str:
        filtered_info = {k: v for k, v in business_info.items() if v is not None}
        filtered_info = json.loads(
            json.dumps(filtered_info, cls=DecimalEncoder), parse_float=Decimal
        )

        try:
            table.put_item(
                Item={
                    "PK": f"business#{business_id}",
                    "SK": "info",
                    "created_at": created_at_isoformat
                    if created_at_isoformat
                    else datetime.utcnow().isoformat(),
                    **filtered_info,
                },
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
            return "insert"
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                (
                    update_expr,
                    attr_values,
                    attr_names,
                ) = build_update_params_for_attributes(filtered_info)
                table.update_item(
                    Key={"PK": f"business#{business_id}", "SK": "info"},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=attr_values,
                    ExpressionAttributeNames=attr_names,
                )
                return "update"
            else:
                raise
