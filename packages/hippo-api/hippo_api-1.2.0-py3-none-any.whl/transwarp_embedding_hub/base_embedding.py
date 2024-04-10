from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    """Interface for embedding models."""

    # Check if the model is available
    def check_model_active(self, **kwargs) -> bool:
        """
                Check if the model is available.

                Parameters:
                    Custom parameters

                Returns:
                    bool: Returns True if the model is available; otherwise, returns False.
        """

        pass

    # Convert string to vector
    def embed_string(self, text: str, **kwargs):
        """
                Converts a string to a vector.

                Parameters:
                    text (str): The text to be converted.
                    Custom parameters

                Returns:
                    list: The embedding vector of the text.
        """

        pass
