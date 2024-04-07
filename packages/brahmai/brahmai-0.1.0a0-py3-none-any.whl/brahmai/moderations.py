import httpx
from ._globals import BASE_URL
import os as _os
from tqdm import tqdm
import json


class Moderations:
    def __init__(self, apikey: str, api_version: str, timeout: int) -> None:
        self.apikey = apikey
        self.api_version = api_version
        self.timeout = timeout
        
    
    def get(self, text: str) -> None:
        if text is not "":
            d_ = json.dumps({
                "input": text
            })

            h_ = {
                "Content-Type": "application/json",
                "brahmai-authentication": self.apikey,
                "brahmai-api_v": self.api_version
            }

            client = httpx.Client(timeout=self.timeout)

            try:
                response = client.post(
                    f"{BASE_URL}moderations",
                    data=d_,
                    headers=h_
                )

                if response.status_code == 200:
                    r_ = response.json()
                    return r_
            except httpx.RequestError as e:
                print("We couldn't connect to the API.")
            finally:
                client.close()