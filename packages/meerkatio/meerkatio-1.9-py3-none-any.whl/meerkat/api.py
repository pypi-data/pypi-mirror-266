import requests
import json

MEERKAT_BASE_URL = "https://meerkatio.com/"
#MEERKAT_BASE_URL = "http://127.0.0.1:5000/"

def send_meerkat_notification(notification_type: str, token: str, message: str):
    response = requests.post(MEERKAT_BASE_URL + "api/notification/send", json={
        "method": notification_type,
        "meerkat_token": token,
        "message": message
    })
    if response.status_code != 200:
        print(f"MeerkatIO Error: {response.text}")

def get_user_token(email, password):
    response = requests.post(MEERKAT_BASE_URL + "api/user/token", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return json.loads(response.text).get("token")
    else:
        return None