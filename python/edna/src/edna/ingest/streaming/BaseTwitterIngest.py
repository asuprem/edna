from __future__ import annotations
from edna.ingest.streaming import BaseStreamingIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.serializers.EmptySerializer import EmptyStringSerializer

from urllib.parse import urlencode
import requests
from typing import Generator, List, Dict

class BaseTwitterIngest(BaseStreamingIngest):
    """Base class for streaming or filtering from Twitter using the v2 API endpoints. Subclasses can use additional
    *args and **kwargs in the `setup()` method.

    Attributes:
        tweet_fields (Dict[str, type]): Valid keys for tweet.fields from the twitter streaming API
        user_fields (Dict[str, type]): Valid keys for user.fields from the twitter streaming API
        media_fields (Dict[str, type]): Valid keys for media.fields from the twitter streaming API
        poll_fields (Dict[str, type]): Valid keys for poll.fields from the twitter streaming API
        place_fields (Dict[str, type]): Valid keys for place.fields from the twitter streaming API
        base_url (str): The endpoint for the streaming or filter request.

    Raises:
        Exception: If the instance cannot connect to the API endpoint.
        NotImplementedError: If `base_url` is not set up in the inheriting class.
        ValueError: Incorrectly formatted `base_url`

    Yields:
        (obj): A call to `__next__()` will yield a single record from the stream.
    """
    tweet_fields: Dict[str,type] = {    "id": str, "text": str, "attachments": dict, "author_id": str, "context_annotations": list, "conversation_id": str,
                        "created_at":str, "entities": dict, "geo": dict, "in_reply_to_user_id": str, "lang": str, "possibly_sensitive": bool,
                        "public_metrics": dict, "referenced_tweets": list, "source": str, "withheld": dict
                        }
    user_fields: Dict[str,type] =  {     "id": str, "name": str, "username": str, "created_at": str, "description": str, "entities": dict, "location": str,
                        "pinned_tweet_id": str, "profile_image_url": str, "protected":bool, "public_metrics": dict, "url": str, "verified": bool,
                        "withheld": dict
                        }
    media_fields: Dict[str,type] = {    "media_key": str, "type": str, "duration_ms": int, "height": int, "preview_image_url": str, "public_metrics": dict, 
                        "width": int
                        }
    poll_fields: Dict[str,type] =  {     "id": str, "options": list, "duration_minutes": int, "end_datetime": "str", "voting_status": str
                        }
    place_fields: Dict[str,type] = {    "full_name": str, "id": str, "contained_within": list, "country": str, "country_code": str, "geo": dict, "name": str,
                        "place_type": str
                        }

    base_url : str

    def __init__(self, serializer: EmptyStringSerializer, bearer_token: str, tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                    poll_fields: List[str] = None, place_fields: List[str] = None, *args, **kwargs):
        """Initializes the BaseTwitterIngest class with the `bearer_token` for authentication and 
        query fields to populate the received tweet object 

        Args:
            serializer (EmptyStringSerializer): An empty serializer for convention.
            bearer_token (str): The authenticating v2 bearer token from a Twitter Developer account.
            tweet_fields (List[str], optional): List of tweet fields to retrieve. Defaults to None.
            user_fields (List[str], optional): List of user fields to retrieve. Defaults to None.
            media_fields (List[str], optional): List of media fields to retrieve. Defaults to None.
            poll_fields (List[str], optional): List of poll fields to retrieve. Defaults to None.
            place_fields (List[str], optional): List of place fields to retrieve. Defaults to None.
        """

        tweet_fields = self.verify_fields(tweet_fields, self.tweet_fields)
        user_fields = self.verify_fields(user_fields, self.user_fields)
        media_fields = self.verify_fields(media_fields, self.media_fields)
        poll_fields = self.verify_fields(poll_fields, self.poll_fields)
        place_fields = self.verify_fields(place_fields, self.place_fields)

        self.url = self.build_url(tweet_fields, user_fields, media_fields, poll_fields, place_fields)
        self.bearer_token = bearer_token
        self.headers = self.create_headers(self.bearer_token)
        self.running = False
        self.response = Generator
        self.setup(*args, **kwargs)
        super().__init__(serializer=serializer, *args, **kwargs)

    def next(self):
        """Sets up a connection to the Twitter API endpoint and retrieves records

        Returns:
            (obj): A single record from the Twitter stream
        """
        if not self.running:
            self.response = self.build_response()
            self.running = True
        return next(self.response)
            
    def build_response(self):
        """Builds a response object to connect to the Twitter stream and returns a generator to yield records.

        Raises:
            Exception: If the instance cannot connect to the API endpoint.

        Yields:
            (Generator): A response generator the yields records from the Twitter stream.
        """
        response = requests.request("GET", self.url, headers= self.headers, stream=True)
        if response.status_code != 200:
            raise Exception("Cannot get stream (HTTP {}): {}".format(response.status_code, response.text))
        for record in response.iter_lines():
            yield record

    def verify_fields(self, passed_field: List[str], referenced_field: Dict[str, str]):
        """A helper function to verify the requested fields.

        Args:
            passed_field (List[str]): The passed list of requested fields.
            referenced_field (Dict[str, str]): The internal fields to compare against.

        Returns:
            (List / None): Returns the filtered list of fields or None if no fields are valid.
        """
        if passed_field is not None:
            valid_fields = [item for item in passed_field if item in referenced_field]
            if len(valid_fields) > 0:
                return valid_fields
        return None

    def build_url(self, tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                        poll_fields: List[str] = None, place_fields: List[str] = None):
        """Helper function to build the query url

        Args:
            tweet_fields (List[str], optional): List of tweet fields to retrieve. Defaults to None.
            user_fields (List[str], optional): List of user fields to retrieve. Defaults to None.
            media_fields (List[str], optional): List of media fields to retrieve. Defaults to None.
            poll_fields (List[str], optional): List of poll fields to retrieve. Defaults to None.
            place_fields (List[str], optional): List of place fields to retrieve. Defaults to None.

        Raises:
            NotImplementedError: If `base_url` is not set up in the inheriting class.
            ValueError: Incorrectly formatted `base_url`

        Returns:
            (str): Properly formatted url for streaming records.
        """
        if self.base_url is None:
            raise NotImplementedError
        if self.base_url[-1] != "?":
            raise ValueError("Base URL does not end with '?': {base_url}".format(base_url = self.base_url))
        vars = {    "tweet.fields":tweet_fields, 
                    "user.fields":user_fields, 
                    "place.fields":place_fields,
                    "media.fields":media_fields,
                    "poll.fields":poll_fields   }
        vars = {item:",".join(vars[item]) for item in vars if vars[item] is not None}
        encoded_suffix = urlencode(vars)
        if len(encoded_suffix):
            return self.base_url+urlencode(vars)
        else:
            return self.base_url[:-1]

    def create_headers(self, bearer_token: str):
        """Helper function to create headers for a request.

        Args:
            bearer_token (str): Authenticating v2 bearer token.

        Returns:
            (dict): Header object
        """
        return {"Authorization": "Bearer {}".format(bearer_token)}

    def setup(self, *args, **kwargs):
        pass
