from ebka.ingest.streaming import StreamingIngestBase
from ebka.process import BaseProcess
from ebka.emit import BaseEmit
from ebka.serializers.EmptySerializer import EmptyStringSerializer

from urllib.parse import urlencode
import requests
from typing import List, Dict

class TwitterIngestBase(StreamingIngestBase):
    tweet_fields = {    "id": str, "text": str, "attachments": dict, "author_id": str, "context_annotations": list, "conversation_id": str,
                        "created_at":str, "entities": dict, "geo": dict, "in_reply_to_user_id": str, "lang": str, "possibly_sensitive": bool,
                        "public_metrics": dict, "referenced_tweets": list, "source": str, "withheld": dict
                        }
    user_fields =  {     "id": str, "name": str, "username": str, "created_at": str, "description": str, "entities": dict, "location": str,
                        "pinned_tweet_id": str, "profile_image_url": str, "protected":bool, "public_metrics": dict, "url": str, "verified": bool,
                        "withheld": dict
                        }
    media_fields = {    "media_key": str, "type": str, "duration_ms": int, "height": int, "preview_image_url": str, "public_metrics": dict, 
                        "width": int
                        }
    poll_fields =  {     "id": str, "options": list, "duration_minutes": int, "end_datetime": "str", "voting_status": str
                        }
    place_fields = {    "full_name": str, "id": str, "contained_within": list, "country": str, "country_code": str, "geo": dict, "name": str,
                        "place_type": str
                        }

    base_url = None

    def __init__(self, serializer: EmptyStringSerializer, bearer_token: str, tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                    poll_fields: List[str] = None, place_fields: List[str] = None, *args, **kwargs):

        tweet_fields = self.verify_fields(tweet_fields, self.tweet_fields)
        user_fields = self.verify_fields(user_fields, self.user_fields)
        media_fields = self.verify_fields(media_fields, self.media_fields)
        poll_fields = self.verify_fields(poll_fields, self.poll_fields)
        place_fields = self.verify_fields(place_fields, self.place_fields)

        self.url = self.build_url(tweet_fields, user_fields, media_fields, poll_fields, place_fields)
        self.bearer_token = bearer_token
        self.headers = self.create_headers(self.bearer_token)
        self.setup(*args, **kwargs)
        super().__init__(serializer=serializer)

    def verify_fields(self, passed_field: List[str], referenced_field: Dict[str, str]):
        if passed_field is not None:
            valid_fields = [item for item in passed_field if item in referenced_field]
            if len(valid_fields) > 0:
                return valid_fields
        return None

    def build_url(self, tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                        poll_fields: List[str] = None, place_fields: List[str] = None):
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
        return {"Authorization": "Bearer {}".format(bearer_token)}

    def stream(self, process: BaseProcess, emitter: BaseEmit):
        response = requests.request("GET", self.url, headers= self.headers, stream=True)
        if response.status_code != 200:
            raise Exception(
                "Cannot get stream (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        for response_line in response.iter_lines():
            if response_line:
                emitter(process(self.serializer.read(response_line))) # TODO change this so user does NOT have to write stream function -- they need to write a setup-stream function or something like that
    def setup(self, *args, **kwargs):
        pass
