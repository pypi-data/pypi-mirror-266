import httpx
from ._globals import BASE_URL
import os as _os
from tqdm import tqdm
import json


class Chat:
    def __init__(self, apikey: str, api_version: str, timeout: int) -> None:
        self.apikey = apikey
        self.api_version = api_version
        self.timeout = timeout
        self.history = []
        self.threads = []

    def clear_history(self):
        self.history = []
        return True

    def list_models(self):
        client = httpx.Client(timeout=self.timeout)
        try:
            response = client.get(
                f"{BASE_URL}models"
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request to DEEPNIGHT failed with status code {response.status_code}")
                print("DEEPNIGHT Response:", response.text)
        except httpx.RequestError as e:
            print("We couldn't connect to the API.")

        finally:
            client.close()

    def create(
        self,
        engine: str,
        temperature: float = 0.3,
        presence_penalty: float = 1.0,
        functions: list = None,
        stream: bool = False,
        auto_decisions: bool = False
    ) -> None:
        d_ = json.dumps({
            "engine": engine,
            "messages": self.history,
            "temperature": temperature,
            "presence_penalty": presence_penalty if presence_penalty else 1,
            "functions": functions if functions else None,
            "auto_decisions": auto_decisions if auto_decisions else None,
            "stream": stream if stream else False
        })

        h_ = {
            "Content-Type": "application/json",
            "brahmai-authorization": self.apikey,
            "brahmai-api_v": self.api_version
        }

        client = httpx.Client(timeout=self.timeout)

        try:
            if not stream:
                response = client.post(
                    f"{BASE_URL}chat",
                    data=d_,
                    headers=h_
                )

                if response.status_code == 200:
                    r_ = response.json()
                    self.history.append({
                        "role": "assistant",
                        "content": r_["response"]["content"]
                    })
                    return response.json()
                else:
                    print(f"Request to DEEPNIGHT failed with status code {response.status_code}")
                    print("DEEPNIGHT Response content:", response.text)
        
        except httpx.RequestError as e:
            print("We couldn't connect to the API.")

        finally:
            client.close()