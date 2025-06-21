import asyncio
import os
import base64
import datetime
import json
from typing import Dict
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from dotenv import load_dotenv
import httpx

load_dotenv()

RUSTORE_KEY_ID = os.getenv("RUSTORE_KEY_ID")
RUSTORE_PRIVATE_KEY = os.getenv("RUSTORE_PRIVATE_KEY")
RUSTORE_APP_ID = os.getenv("RUSTORE_APP_ID")
RUSTORE_PACKAGE_NAME = os.getenv("RUSTORE_PACKAGE_NAME")


def generate_signature(key_id, private_key_content):
    private_key = RSA.import_key(base64.b64decode(private_key_content))
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="milliseconds"
    )
    message_to_sign = key_id + timestamp
    print("Message to sign:", message_to_sign)

    hash_obj = SHA512.new(message_to_sign.encode())
    signer = pkcs1_15.new(private_key)
    signature_bytes = signer.sign(hash_obj)
    signature_value = base64.b64encode(signature_bytes).decode()

    return {"keyId": key_id, "timestamp": timestamp, "signature": signature_value}


async def auth():
    if not RUSTORE_KEY_ID or not RUSTORE_PRIVATE_KEY or not RUSTORE_APP_ID:
        raise ValueError("Environment variables for Rustore are not set")

    params = generate_signature(RUSTORE_KEY_ID, RUSTORE_PRIVATE_KEY)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://public-api.rustore.ru/public/auth/",
            headers={
                "Content-Type": "application/json",
            },
            json=params,
        )
    if response.status_code != 200:
        raise Exception(
            f"Failed to authenticate: {response.status_code} {response.text}"
        )

    return response.json()["body"]["jwe"] or None


async def get_current_version() -> Dict[str, str]:
    if not RUSTORE_PACKAGE_NAME:
        raise ValueError("RUSTORE_PACKAGE_NAME environment variable is not set")

    public_token = await auth()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://public-api.rustore.ru/public/v1/application/{RUSTORE_PACKAGE_NAME}/version",
            headers={
                "Public-Token": public_token,
                "Content-Type": "application/json",
            },
            params={
                "filterTestingType": "RELEASE",
            },
        )
    if response.status_code != 200:
        raise Exception(
            f"Failed to get version: {response.status_code} {response.text}"
        )
    
    version_obj = response.json()["body"]['content'][0]

    return {
        "version_name": version_obj["versionName"],
        "version_code": version_obj["versionCode"]
    }

