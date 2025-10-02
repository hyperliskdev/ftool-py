from falconpy import APIHarnessV2
import dotenv

def get_client():
    api = dotenv.load_dotenv(".env")

    if api is False:
        raise Exception("Failed to load .env file")
    
    client_id = dotenv.get_key(".env", "FALCON_CLIENT_ID")
    client_secret = dotenv.get_key(".env", "FALCON_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise Exception("FALCON_CLIENT_ID or FALCON_CLIENT_SECRET not found in .env file")


    return APIHarnessV2(client_id=client_id, client_secret=client_secret)