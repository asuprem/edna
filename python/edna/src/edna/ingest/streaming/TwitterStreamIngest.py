from edna.ingest.streaming import TwitterIngestBase
from typing import List
from edna.serializers.EmptySerializer import EmptyStringSerializer

class TwitterStreamIngest(TwitterIngestBase):
    base_url = "https://api.twitter.com/2/tweets/sample/stream?"
 
    