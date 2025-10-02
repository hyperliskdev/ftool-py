from falconpy import APIHarnessV2
import dotenv

def get_client():
    api = dotenv.load_dotenv(".env")
    client_id = api.get("FALCON_CLIENT_ID")
    client_secret = api.get("FALCON_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("FALCON_CLIENT_ID and FALCON_CLIENT_SECRET must be set in the .env file")

    return APIHarnessV2(client_id=client_id, client_secret=client_secret)