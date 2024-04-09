class PricingData:
    """
    A class for handling pricing data in JSON format.

    Parameters:
    - json_data (dict): The pricing data in JSON format.

    Attributes:
    - data (dict): The pricing data as a dictionary.

    Methods:
    - get_release_date(): Get the release date from the pricing data.
    - get_language_model_pricing(model_name=None): Get pricing information for language models.
    - get_assistants_api_pricing(tool_name=None): Get pricing information for the assistants API.
    - get_fine_tuning_model_pricing(model_name=None): Get pricing information for fine-tuning models.
    - get_embedding_model_pricing(model_name=None): Get pricing information for embedding models.
    - get_base_model_pricing(model_name=None): Get pricing information for base models.
    - get_image_model_pricing(model_name=None): Get pricing information for image models.
    - get_audio_model_pricing(model_name=None): Get pricing information for audio models.
    """
    def __init__(self, json_data):
        """
        Initializes the PricingData with JSON data.

        Parameters:
            json_data (dict): A dictionary containing the pricing data.
        """
        self.data = json_data

    def get_release_date(self):
        """
        Retrieves the release date of the pricing data.

        Returns:
            str: The release date.
        """
        return self.data.get("release_date")

    def get_language_model_pricing(self, model_name=None):
        """
        Retrieves the pricing information for language models.

        Parameters:
            model_name (str, optional): The name of the specific language model. Default is None.

        Returns:
            dict or None: Pricing information for the specified language model or all models if none specified.
        """
        models = self.data["pricing"]["language_models"]
        return models.get(model_name) if model_name else models

    def get_assistants_api_pricing(self, tool_name=None):
        """
        Retrieves pricing information for assistants API.

        Parameters:
            tool_name (str, optional): The name of the specific assistant tool. Default is None.

        Returns:
            dict or None: Pricing information for the specified assistant tool or all tools if none specified.
        """
        tools = self.data["pricing"]["assistants_api"]
        return tools.get(tool_name) if tool_name else tools

    def get_fine_tuning_model_pricing(self, model_name=None):
        """
        Retrieves pricing information for fine-tuning models.

        Parameters:
            model_name (str, optional): The name of the specific fine-tuning model. Default is None.

        Returns:
            dict or None: Pricing information for the specified fine-tuning model or all models if none specified.
        """
        models = self.data["pricing"]["fine_tuning_models"]
        return models.get(model_name) if model_name else models

    def get_embedding_model_pricing(self, model_name=None):
        """
        Retrieves pricing information for embedding models.

        Parameters:
            model_name (str, optional): The name of the specific embedding model. Default is None.

        Returns:
            dict or None: Pricing information for the specified embedding model or all models if none specified.
        """
        models = self.data["pricing"]["embedding_models"]
        return models.get(model_name) if model_name else models

    def get_base_model_pricing(self, model_name=None):
        """
        Retrieves pricing information for base models.

        Parameters:
            model_name (str, optional): The name of the specific base model. Default is None.

        Returns:
            dict or None: Pricing information for the specified base model or all models if none specified.
        """
        models = self.data["pricing"]["base_models"]
        return models.get(model_name) if model_name else models

    def get_image_model_pricing(self, model_name=None):
        """
        Retrieves pricing information for image models.

        Parameters:
            model_name (str, optional): The name of the specific image model. Default is None.

        Returns:
            dict or None: Pricing information for the specified image model or all models if none specified.
        """
        models = self.data["pricing"]["image_models"]
        return models.get(model_name) if model_name else models

    def get_audio_model_pricing(self, model_name=None):
        """
        Retrieves pricing information for audio models.

        Parameters:
            model_name (str, optional): The name of the specific audio model. Default is None.

        Returns:
            dict or None: Pricing information for the specified audio model or all models if none specified.
        """
        models = self.data["pricing"]["audio_models"]
        return models.get(model_name) if model_name else models