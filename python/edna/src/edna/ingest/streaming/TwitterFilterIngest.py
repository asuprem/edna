from edna.ingest.streaming import TwitterIngestBase
from edna.serializers.EmptySerializer import EmptyStringSerializer
import requests
from typing import List, Dict

class TwitterFilterIngest(TwitterIngestBase):
    base_url = "https://api.twitter.com/2/tweets/search/stream?"
    def __init__(self, serializer: EmptyStringSerializer, bearer_token: str, filters: List[str], tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                    poll_fields: List[str] = None, place_fields: List[str] = None, *args, **kwargs):
        super().__init__(serializer, bearer_token, tweet_fields, user_fields, media_fields, poll_fields, place_fields, *args, **kwargs)
        self.delete_all_filters(self.get_filters())
        self.set_filters(filters)

    def get_filters(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get filters (HTTP {}): {}".format(response.status_code, response.text)
            )
        return response.json()

    def delete_all_filters(self, filters: Dict[str, str]):
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

    
    

    