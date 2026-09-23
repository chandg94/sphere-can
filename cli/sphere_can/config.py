import os

DEFAULT_API = "http://172.30.0.11:8000"

def api_base():
    return os.environ.get("SPHERE_API", DEFAULT_API)

def ws_base():
    return api_base().replace("http", "ws")
