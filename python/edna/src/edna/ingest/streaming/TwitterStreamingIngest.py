from edna.ingest.streaming.BaseTwitterIngest import BaseTwitterIngest

class TwitterStreamingIngest(BaseTwitterIngest):
    base_url = "https://api.twitter.com/2/tweets/sample/stream?"