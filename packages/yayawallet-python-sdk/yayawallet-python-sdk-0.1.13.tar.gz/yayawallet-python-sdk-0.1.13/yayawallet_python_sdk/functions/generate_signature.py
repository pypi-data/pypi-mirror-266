import hashlib
import hmac
import base64
import os

def generate_signature(timestamp, method, endpoint, body):
    prehash_string = timestamp + method + endpoint + body
    api_secret = os.getenv("YAYA_API_SECRET")
    hashed_key = hmac.new(bytes(api_secret, 'UTF-8'), msg=bytes(prehash_string, 'UTF-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(hashed_key).decode()
    return signature