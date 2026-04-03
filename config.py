import os

YGG_SERVER_IP = os.getenv("YGG_SERVER_IP", "")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

BASE_URL = f"http://[{YGG_SERVER_IP}]:{SERVER_PORT}"
WS_URL = f"ws://[{YGG_SERVER_IP}]:{SERVER_PORT}"