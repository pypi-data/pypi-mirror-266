from transwarp_embedding_hub.base_embedding import *
import os
import yaml
import openai


class Azure(BaseEmbedding):
    """openai embedding strategy."""

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(dir_path, 'config.yaml')
        with open(config_path) as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)['model']['azure']
        self.openai_api_key = self.config['apikey']
        self.embedding_engine = self.config['engine']
        self.openai_api_version = self.config['version']
        self.openai_api_url = self.config['url']

    # Check if the model is available
    def check_model_active(self, api_key: str = None, embedding_engine: str = None):

        """
                        Check if the model is available.

                        Parameters:
                            url: The IP and port of the server where the model is located, for example: 127.0.0.0:1111
                            route_path: The address of the model on this server

                        Returns:
                            Returns True if successful, otherwise returns an error message and False.
        """

        try:
            self.embed_string("你好", api_key, embedding_engine)
            return True
        except Exception as e:
            print(f"Model not available. Error: {e}")
            return False

    # Convert string to vector
    def embed_string(self, text: str, api_key: str = None, embedding_engine: str = None, api_base: str = None,
                     api_version: str = None):

        """
                        Text to vector.

                        Parameters:
                            url: The IP and port of the server where the model is located, for example: 127.0.0.0:1111
                            route_path: The address of the model on this server

                        Returns:
                            Returns a vector list[float] if successful, otherwise returns an error message.
        """


        if api_key is None:
            api_key = self.openai_api_key
        else:
            api_key = api_key

        if embedding_engine is None:
            embedding_engine = self.embedding_engine
        else:
            embedding_engine = embedding_engine

        if api_base is None:
            api_base = self.openai_api_url
        else:
            api_base = api_base

        if api_version is None:
            api_version = self.openai_api_version
        else:
            api_version = api_version

        openai.api_type = "azure"
        openai.api_key = api_key
        openai.api_base = api_base
        openai.api_version = api_version
        return openai.Embedding.create(
            input=text,
            engine=embedding_engine)["data"][0]["embedding"]
