from edna.ingest.streaming.BaseTwitterIngest import BaseTwitterIngest

class TwitterStreamingIngest(BaseTwitterIngest):
    """Class for streaming from Twitter using the v2 API endpoints.

    Attributes:
        base_url (str): The endpoint for the streaming or filter request.
    """
    base_url = "https://api.twitter.com/2/tweets/sample/stream?"