from transwarp_embedding_hub.openai import *
from transwarp_embedding_hub.pulse import *
from transwarp_embedding_hub.azure import *


class EmbeddingHub:
    """Factory for embedding strategy."""

    def __init__(self, model_name):
        self.model_name = model_name

    # Get embedding strategy based on parameters
    def get_strategy(self):

        Strategy = {
            'openai': OpenAI(),
            'TranswarpVectorPulse': TranswarpVectorPulse(),
            'azure': Azure()
        }.get(self.model_name)


        # If there is no matching type, return 'no match model'
        if not Strategy:
            raise ValueError('no match model')
        else:
            return Strategy
