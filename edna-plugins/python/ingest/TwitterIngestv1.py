from edna.ingest.streaming import StreamingIngestBase
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.serializers.EmptySerializer import EmptyStringSerializer

from tweepy import OAuthHandler, Stream, StreamListener
from sys import stdout

class TwitterIngestv1(StreamingIngestBase):
    def __init__(self, serializer: EmptyStringSerializer, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        super().__init__(serializer=serializer)

    def stream(self, process: BaseProcess, emitter: BaseEmit):
        self.listener = self.Listener(process, emitter)
        self.t_stream = Stream(self.auth, self.listener)
        self.t_stream.sample()

    class Listener(StreamListener):
        """ A tweepy StreamListener handles tweets that are received from the stream.
        """
        def __init__(self, process: BaseProcess, emitter: BaseEmit):
            self.process = process
            self.emitter = emitter
            super().__init__()
        def on_data(self, data):
            self.emitter(self.process(data))

        def on_error(self, status):
            print(status, file = stdout) 

    