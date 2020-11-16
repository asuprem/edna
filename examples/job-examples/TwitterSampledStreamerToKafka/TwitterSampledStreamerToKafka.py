import logging
from edna.api import StreamBuilder
from edna.core.execution.context import StreamingContext
from edna.ingest.streaming import TwitterStreamingIngest
from edna.process import BaseProcess
from edna.emit import KafkaEmit

def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")
    
    context = StreamingContext()
    
    stream = StreamBuilder.build(
        TwitterStreamingIngest(
            bearer_token=context.getVariable("bearer_token"), 
            tweet_fields=context.getVariable("tweet_fields"), 
            user_fields=context.getVariable("user_fields"), 
            place_fields=context.getVariable("place_fields"), 
            media_fields=context.getVariable("media_fields"))
    ).emit(
        KafkaEmit(
            kafka_topic=context.getVariable("kafka_topic"), 
            bootstrap_server=context.getVariable("bootstrap_server"),
            bootstrap_port=context.getVariable("bootstrap_port"))
    )
        
    context.addStream(stream)    
    
    context.execute()

if  __name__=="__main__":
    main()