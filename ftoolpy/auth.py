from falconpy import APIHarnessV2
import os

def get_client():
    client_id = os.getenv("FALCON_CLIENT_ID")
    client_secret = os.getenv("FALCON_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Missing FALCON_CLIENT_ID or FALCON_CLIENT_SECRET in environment.")

    return APIHarnessV2(client_id=client_id, client_secret=client_secret)