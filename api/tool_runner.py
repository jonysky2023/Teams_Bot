import os
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = os.getenv("API_BASEURL")
USER = os.getenv("API_USER")
PASS = os.getenv("API_PASS")


def run_tool(name, input_data):

    auth = HTTPBasicAuth(USER, PASS)

    if name == "get_device_status":
        url = f"{BASE_URL}/device/status"
        params = {"device": input_data["device"]}

        res = requests.get(url, params=params, auth=auth)
        return res.json()

    if name == "get_service_status":
        url = f"{BASE_URL}/service/status"
        params = {
            "device": input_data["device"],
            "service": input_data["service"]
        }

        res = requests.get(url, params=params, auth=auth)
        return res.json()

    raise Exception(f"Tool no soportada: {name}")
