import requests
from dataclasses import dataclass, field
import json

@dataclass
class TxStore:
    blockchain_id: int
    env:str = "test"
    base_url:str = field(init=False)

    def __post_init__(self):
        self.base_url = f"https://txstore.btcs{self.env}.net/{self.blockchain_id}/api"

    def get_health(self):
        response = requests.get(f"{self.base_url}/health")
        return response
    
    def truncate(self, address, height):
        url = f"{self.base_url}/v1/Address/truncateAndReupdate"

        headers = {
            'Content-Type': 'application/json'
        }
        body = json.dumps({
            "address": address,
            "includingHeight": height
        })
        response = requests.patch(url, headers=headers, data=body)
        return response


if __name__ == "__main__":
    txstore = TxStore(blockchain_id=18)
    print(txstore.truncate("0x0001ac1974dbec2b13dc133da8352ecc145ab342", 0).status_code)