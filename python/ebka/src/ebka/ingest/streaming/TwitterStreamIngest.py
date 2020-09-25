from ebka.ingest.streaming import TwitterIngestBase
from typing import List
from ebka.serializers.EmptySerializer import EmptyStringSerializer

class TwitterStreamIngest(TwitterIngestBase):
    base_url = "https://api.twitter.com/2/tweets/sample/stream?"

    def __init__(self, serializer: EmptyStringSerializer, bearer_token: str, tweet_fields: List[str] = None, user_fields: List[str] = None, media_fields: List[str] = None, 
                    poll_fields: List[str] = None, place_fields: List[str] = None, *args, **kwargs):
        super().__init__(serializer, bearer_token, tweet_fields, user_fields, media_fields, poll_fields, place_fields, *args, **kwargs)

    
 
    