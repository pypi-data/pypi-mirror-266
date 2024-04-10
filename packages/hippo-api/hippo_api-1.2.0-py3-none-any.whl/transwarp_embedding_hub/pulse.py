from transwarp_embedding_hub.base_embedding import *
import os
import yaml
import json
import requests


class TranswarpVectorPulse(BaseEmbedding):
    """TranswarpVectorPulse embedding strategy."""

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(dir_path, 'config.yaml')
        with open(config_path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)['model']['TranswarpVectorPulse']
        self.server_url = config['url']
        self.route_path = config['route_path']
        self.model_name = config['model_name']
        self.request_template = {
            "id": "1",
            "inputs": [
                {
                    "name": "TEXT_BINARY",
                    "shape": [1],
                    "datatype": "BYTES",
                    "parameters": {"binary_data_size": 0}
                },
                {"name": "TEXT_DESC",
                 "shape": [1],
                 "datatype": "BYTES",
                 "parameters": {"binary_data_size": 0}
                 }
            ],
            "outputs": [{"name": "RESULT", "parameters": {"binary_data": True}}]
        }

    def _make_input_text(self, input_text: str):
        input_bytes = input_text.encode('utf-8')
        input_len = len(input_bytes)
        input_bytes = input_len.to_bytes(4, "little") + input_bytes

        img_json_raw = {
            'client_id': 'example',
            'params': [
                {
                    'id': '0',
                    'type': 'jpeg',
                    'data': 'IMAGE_BINARY'
                }
            ]
        }
        img_json_bytes = json.dumps(img_json_raw).encode()
        img_json_len = len(img_json_bytes)

        img_json_bytes = img_json_len.to_bytes(4, "little") + img_json_bytes
        self.request_template['inputs'][0]['parameters']['binary_data_size'] = input_len + 4
        self.request_template['inputs'][1]['parameters']['binary_data_size'] = img_json_len + 4
        request_bytes = json.dumps(self.request_template).encode()
        request_json_len = len(request_bytes)
        request_bytes = request_bytes + input_bytes + img_json_bytes

        return request_bytes, request_json_len

    # Check if the model is available
    def check_model_active(self, url: str = None, route_path: str = None):
        """
                Check if the model is available.

                Parameters:
                    url: The IP and port of the server where the model is located, for example: 127.0.0.0:1111
                    route_path: The address of the model on this server

                Returns:
                    Returns True if successful, otherwise returns an error message and False.
        """

        try:
            self.embed_string("你好", url, route_path)
            return True
        except Exception as e:
            print(f"Model not available. Error: {e}")
            return False

    # Convert string to vector
    def embed_string(self, text: str, url: str = None, route_path: str = None):
        """
                Text to vector.

                Parameters:
                    url: The IP and port of the server where the model is located, for example: 127.0.0.0:1111
                    route_path: The address of the model on this server

                Returns:
                    Returns a vector list[float] if successful, otherwise returns an error message.
        """

        if url is None:
            url = self.server_url
        else:
            url = url

        if route_path is None:
            route_path = self.route_path
        else:
            route_path = route_path

        request_bytes, request_len = self._make_input_text(text)
        request_url = 'http://' + url + route_path.format(self.model_name)

        request_headers = {
            'Content-Type': 'application/octet-stream',
            "Inference-Header-Content-Length": str(request_len)
        }

        res = requests.post(url=request_url, data=request_bytes, headers=request_headers)

        embedding = None

        if res.status_code == requests.codes.ok:
            json_len = int(res.headers["Inference-Header-Content-Length"])
            output_str = bytes.decode(res.content[json_len + 4:])
            output_json = json.loads(output_str)
            embedding = output_json["results"][0]["objects"][0]["attributes"][0]["value"][0]
        else:
            raise ValueError(f"request post faild the status_code is:{res.status_code} the reason is:{res.reason}")
        return embedding
