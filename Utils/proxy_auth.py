import requests
from time import sleep
from Utils.constants import WEBSHARE_API_KEY
def get_ip():
    response = requests.get(
        "https://proxy.webshare.io/api/v2/proxy/ipauthorization/whatsmyip/",
        headers={"Authorization": f"Token {WEBSHARE_API_KEY}"}
    )
    return response.json().get("ip_address")
def create_ip_auth():

    IP_ADDRESS=get_ip()
    response = requests.post(
        "https://proxy.webshare.io/api/v2/proxy/ipauthorization/",
        json={"ip_address": IP_ADDRESS},
        headers={"Authorization": f"Token {WEBSHARE_API_KEY}"})
    print(f'Auth Id: {response.json().get("id")}')
    return response.json().get("id")

def delete_ip_auth(id):
    response = requests.delete(
        f"https://proxy.webshare.io/api/v2/proxy/ipauthorization/{id}/",
        headers={"Authorization": f"Token {WEBSHARE_API_KEY}"}
    )

def delete_all_ip_auths():
    response = requests.get(
        "https://proxy.webshare.io/api/v2/proxy/ipauthorization/",
        headers={"Authorization": f"Token {WEBSHARE_API_KEY}"}
    )
    for x in response.json().get("results"):
        delete_ip_auth(x.get("id"))
        sleep(0.03)