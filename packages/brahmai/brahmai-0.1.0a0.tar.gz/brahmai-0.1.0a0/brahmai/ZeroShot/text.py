import httpx
from .._globals import BASE_URL
import os as _os
from tqdm import tqdm
import json


class ZeroShotClassifier:
    def __init__(self, 
        apikey: str,
        api_version: str, 
        timeout: int) -> None:
        self.apikey = apikey
        self.api_version = api_version
        self.timeout = timeout

    def classifier(self, text: str, classes: list, hypothesis: str="", multi_class: bool=False):
        d_ = json.dumps({
            "text": text,
            "classes": classes,
            "hypothesis": hypothesis,
            "multi_class": multi_class
        })
        h_ = {
            "Content-Type": "application/json",
            "brahmai-authorization": self.apikey,
            "brahmai-api_v": self.api_version
        }

        client = httpx.Client(timeout=self.timeout)

        try:
            response = client.post(
                f"{BASE_URL}zsc/text",
                headers=h_,
                data=d_
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request to BRAHMAI failed with status code: {response.status_code}")
                print(f"BRAHMAI Response: {response.text}")
        except httpx.RequestError as e:
            print("We couldn't connect to the API.")
            raise e
        except Exception as e:
            raise e