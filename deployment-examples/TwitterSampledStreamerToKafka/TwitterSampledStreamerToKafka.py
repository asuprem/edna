from edna.ingest.streaming import TwitterStreamingIngest
from edna.process import BaseProcess
from edna.emit import KafkaEmit
from edna.serializers.EmptySerializer import EmptyStringSerializer
from edna.serializers import StringSerializer
from edna.core.execution.context import StreamingContext

def main():
    
    context = StreamingContext()
    ingest_serializer = EmptyStringSerializer()
    emit_serializer = StringSerializer()
    ingest = TwitterStreamingIngest(serializer=ingest_serializer, bearer_token=context.getVariable("bearer_token"), 
                tweet_fields=context.getVariable("tweet_fields"), 
                user_fields=context.getVariable("user_fields"), 
                place_fields=context.getVariable("place_fields"), 
                media_fields=context.getVariable("media_fields"))
    process = BaseProcess()
    emit = KafkaEmit(serializer=emit_serializer, 
                kafka_topic=context.getVariable("kafka_topic"), 
                bootstrap_server=context.getVariable("bootstrap_server"),
                bootstrap_port=context.getVariable("bootstrap_port"))

    context.addIngest(ingest)
    context.addProcess(process)
    context.addEmit(emit)
    
    context.execute()

if  __name__=="__main__":
    main()