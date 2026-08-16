import boto3

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

class UnauthorizedError(Exception):
    pass

def verify_role(user_id: str, expected_role: str) -> dict:
    user_item = users_table.get_item(Key={"user_id": user_id}).get("Item")
    if user_item is None:
        raise UnauthorizedError(f"User {user_id} not found")
    if user_item.get("role") != expected_role:
        raise UnauthorizedError(f"User {user_id} does not have role {expected_role}")
    return user_item