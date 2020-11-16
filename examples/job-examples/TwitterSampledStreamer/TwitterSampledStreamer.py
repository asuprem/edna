import logging
from edna.ingest.streaming import TwitterStreamingIngest
from edna.emit import StdoutEmit,RecordCounterEmit
from edna.serializers import EmptySerializer
from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder

def main():
    

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")

    context = StreamingContext()
    
    stream = StreamBuilder.build(
        TwitterStreamingIngest(
        bearer_token=context.getVariable("bearer_token"), 
        tweet_fields=context.getVariable("tweet_fields"), 
        user_fields=context.getVariable("user_fields"), 
        place_fields=context.getVariable("place_fields"), 
        media_fields=context.getVariable("media_fields")),
        streaming_context=context
    ).emit(
        StdoutEmit()
    )

    context.addStream(stream=stream)
    context.execute()

if  __name__=="__main__":
    main()