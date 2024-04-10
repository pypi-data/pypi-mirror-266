import json
import requests


class CustomEmbedding:
    """TranswarpVectorPulse embedding strategy."""

    def __init__(self, ip, port, suffix, key):
        self.key = key
        self.url = "http://{}:{}/{}".format(ip, port, suffix)

    # Convert string to vector
    def embed_string(self, text: str):
        data = {self.key: text}
        response = requests.post(self.url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        response_json = response.json()
        output = response_json.get("data")[0].get("embedding")
        return output
