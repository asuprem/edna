from edna.ingest.streaming.BaseTwitterIngest import BaseTwitterIngest
from edna.serializers.EmptySerializer import EmptyStringSerializer
import requests
from typing import List, Dict

class TwitterFilteredIngest(BaseTwitterIngest):
    """Class for streaming from Twitter using the v2 API endpoints.

    Attributes:
        base_url (str): The endpoint for the streaming or filter request.

    Raises:
        Exception: Raised when filters can't be retrieved, deleted, or added
    
    """
    base_url = "https://api.twitter.com/2/tweets/search/stream?"
    def __init__(self, serializer: EmptyStringSerializer, bearer_token: str, filters: List[str], tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                    poll_fields: List[str] = None, place_fields: List[str] = None, *args, **kwargs):
        """Initializes the TwitterFilteredIngest class with the `bearer_token` for authentication and 
        query fields to populate the received tweet object 

        Args:
            serializer (EmptyStringSerializer): An empty serializer for convention.
            filter (List[str]): List of filters to apply during streaming.
            bearer_token (str): The authenticating v2 bearer token from a Twitter Developer account.
            tweet_fields (List[str], optional): List of tweet fields to retrieve. Defaults to None.
            user_fields (List[str], optional): List of user fields to retrieve. Defaults to None.
            media_fields (List[str], optional): List of media fields to retrieve. Defaults to None.
            poll_fields (List[str], optional): List of poll fields to retrieve. Defaults to None.
            place_fields (List[str], optional): List of place fields to retrieve. Defaults to None.
        """
        super().__init__(serializer, bearer_token, tweet_fields, user_fields, media_fields, poll_fields, place_fields, *args, **kwargs)
        self.delete_all_filters(self.get_filters())
        self.set_filters(filters)

    def get_filters(self):
        """Helper function to get the list of filters

        Raises:
            Exception: Raised if existing filters cannot be raised.

        Returns:
            (Dict): Existing filters.
        """
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get filters (HTTP {}): {}".format(response.status_code, response.text)
            )
        return response.json()

    def delete_all_filters(self, filters: Dict[str, str]):
        """Helper function to delete filters.

        Args:
            filters (Dict[str, str]): Filters to delete.

        Raises:
            Exception: Raised if filtered cannot be deleted.
        """
        if filters is None or "data" not in filters:
            return None

        ids = list(map(lambda rule: rule["id"], filters["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            headers=self.headers,
            json=payload
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete filters (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )

    def set_filters(self, filters: List[str]):
        """Helper functions to set new filters.

        Args:
            filters (List[str]): List of filters to set.

        Raises:
            Exception: Raised if filters cannot be set.
        """
        filters = [{"value": item} for item in filters]
        payload = {"add": filters}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            headers=self.headers,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add filters (HTTP {}): {}".format(response.status_code, response.text)
            )

    
    

    