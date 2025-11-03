from ninja import Schema, Field


class FCMSchema(Schema):
    fcm_token: str = Field(min_length=10, max_length=4096)
    client_name: str