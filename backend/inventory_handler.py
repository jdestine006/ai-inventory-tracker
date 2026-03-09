import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3

# AWS clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

sns = boto3.client("sns")


# -------------------------
# Utility Functions
# -------------------------

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
        },
        "body": json.dumps(body, default=decimal_default)
    }


def parse_body(event):
    body = event.get("body")
    if not body:
        return {}
    return json.loads(body)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# -------------------------
# Bedrock AI Summary
# -------------------------

def generate_inventory_summary(items):

    if not items:
        return "Inventory is currently empty. No stock risks detected."

    prompt = f"""
You are an inventory analyst.

Review the following inventory items and provide:

1. A short summary of overall inventory health
2. Which items are low stock
3. Which items may need restocking soon
4. Any useful observations

Inventory data:
{json.dumps(items, default=decimal_default)}

Keep the response concise and business friendly.
"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 300,
            "temperature": 0.3
        }
    }

    bedrock_response = bedrock_runtime.invoke_model(
        modelId=os.environ["MODEL_ID"],
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(bedrock_response["body"].read())

    print("BEDROCK RAW RESPONSE:", json.dumps(result))

    return result["output"]["message"]["content"][0]["text"]

### PUBLISH INVENTORY FUNCTION 

def publish_inventory_alert(summary, items):
    low_stock_items = [
        item for item in items
        if int(item.get("quantity", 0)) <= int(item.get("reorderThreshold", 0))
    ]

    subject = "Daily Inventory Health Report"

    lines = [
        "AI Inventory Health Report",
        "",
        f"Total items: {len(items)}",
        f"Low stock items: {len(low_stock_items)}",
        "",
        "Summary:",
        summary,
    ]

    if low_stock_items:
        lines.extend(["", "Low stock items:"])
        for item in low_stock_items:
            lines.append(
                f"- {item.get('name')} "
                f"(qty: {item.get('quantity')}, threshold: {item.get('reorderThreshold')})"
            )

    message = "\n".join(lines)

    print("SNS_TOPIC_ARN:", os.environ["SNS_TOPIC_ARN"])

    sns.publish(
        TopicArn=os.environ["SNS_TOPIC_ARN"],
        Subject=subject,
        Message=message,
    )


# -------------------------
# Lambda Handler
# -------------------------

def lambda_handler(event, context):

    print("EVENT:", json.dumps(event, default=decimal_default))

    # -------------------------
    # EventBridge Scheduler
    # -------------------------

    if event.get("source") == "aws.scheduler":
        try:
            result = table.scan()
            items = result.get("Items", [])
            summary = generate_inventory_summary(items)

            print("SCHEDULED INVENTORY SUMMARY:")
            print(summary)

            publish_inventory_alert(summary, items)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "scheduled summary generated and emailed",
                    "summary": summary
                })
            }

        except Exception as e:
            print("SCHEDULED SUMMARY ERROR:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "scheduled_summary_failed",
                    "details": str(e)
                })
            }


    # -------------------------
    # API Gateway Routing
    # -------------------------

    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    path_params = event.get("pathParameters") or {}

    print("METHOD:", method)
    print("PATH:", path)
    print("PATH PARAMS:", path_params)

    if method == "OPTIONS":
        return response(200, {"ok": True})

    try:

        # -------------------------
        # Create Item
        # -------------------------

        if method == "POST" and path.endswith("/items"):

            body = parse_body(event)

            name = body.get("name", "").strip()
            category = body.get("category", "").strip()
            quantity = body.get("quantity")
            reorder_threshold = body.get("reorderThreshold")

            if not name:
                return response(400, {"error": "name is required"})

            if quantity is None or reorder_threshold is None:
                return response(400, {"error": "quantity and reorderThreshold required"})

            item_id = str(uuid.uuid4())

            item = {
                "itemId": item_id,
                "name": name,
                "category": category,
                "quantity": int(quantity),
                "reorderThreshold": int(reorder_threshold),
                "lastUpdated": now_iso()
            }

            table.put_item(Item=item)

            return response(200, item)

        # -------------------------
        # Get All Items
        # -------------------------

        if method == "GET" and path.endswith("/items"):

            result = table.scan()

            items = result.get("Items", [])

            items.sort(key=lambda x: x.get("name", "").lower())

            return response(200, {"items": items})

        # -------------------------
        # Update Item
        # -------------------------

        if method == "PUT" and path_params.get("itemId"):

            item_id = path_params["itemId"]

            body = parse_body(event)

            update_expr = []
            expr_values = {}

            for field in ["name", "category", "quantity", "reorderThreshold"]:
                if field in body:
                    update_expr.append(f"{field} = :{field}")
                    expr_values[f":{field}"] = body[field]

            update_expr.append("lastUpdated = :lastUpdated")
            expr_values[":lastUpdated"] = now_iso()

            if len(update_expr) == 1:
                return response(400, {"error": "no fields provided to update"})

            result = table.update_item(
                Key={"itemId": item_id},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeValues=expr_values,
                ReturnValues="ALL_NEW"
            )

            return response(200, result["Attributes"])

        # -------------------------
        # Delete Item
        # -------------------------

        if method == "DELETE" and path_params.get("itemId"):

            item_id = path_params["itemId"]

            table.delete_item(Key={"itemId": item_id})

            return response(200, {
                "message": "item deleted",
                "itemId": item_id
            })

        # -------------------------
        # AI Inventory Summary
        # -------------------------

        if method == "POST" and path.endswith("/inventory-summary"):

            result = table.scan()

            items = result.get("Items", [])

            print("ITEM COUNT:", len(items))

            summary = generate_inventory_summary(items)

            return response(200, {"summary": summary})

        return response(404, {
            "error": "route not found",
            "method": method,
            "path": path,
            "pathParams": path_params
        })

    except Exception as e:

        print("API ERROR:", str(e))

        return response(500, {
            "error": "internal_server_error",
            "details": str(e)
        })
