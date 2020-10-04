# Running Multiple Jobs as a Sequence

This is what we have been building towards, but we will actually cover a complete Application in the next part.

Let's distinguish between an application and a job:

- An EDNA application consists of several Jobs
- An EDNA job is a small executable that contains an Ingest, Process, and Emit primitive

Since EDNA is still WIP, these could change. 

## EDNA Applications

Here are a few guidelines for EDNA Applications. Guidelines, however, is a strong word, since I am basically working this out as I go, so don't take these as set in stone.

- An Application should have at least 1 Source Job that brings a stream from outside the Application
    - The TwitterStreamer is an example of a Source Job
    - I say at least 1 Source Job because we could have multiple streams that we join somewhere in the Application
- An Application should have at least 1 Sink Job that materializes the stream outide the Application
    - Examples of Sink Jobs would be dumping to an S3 bucket, or SQL database
    - An Application could have multiple Sink Jobs -- for example 1 Sink Job near the Source to archive the stream, plus another one near the end of the Application so save the output
- All Jobs of an Application should exist in the same kubernetes namespace
    - This just makes management easier

## The Application for this Step

Right now, we will run the following Application

![architecture](./images/architecture.png)

We will have a human (i.e. you) write strings to Kafka using a Kafka Console Producer. This will simulate an external stream.

A Source Job will read the "external" stream and push it into Kafka.

Then we will have two internal jobs that will just pass through the strings.

Finally, a Sink Job will push the stream to an "external" sink -- we will simulate this as well with a Kafka Console Consumer that will read the stream.

What we are actually learning here is:

- How to set up multiple jobs and their connections with topics
- Serialization pitfalls

## Setting up multiple jobs

We are going to use Kafka as the streaming backbone for all jobs. Kafka operates as a pub/sub interface, where publishers send messages to a **topic**, and subscribers pull messages from the same **topic**.

So within an application, we need to make sure two jobs that need to talk to each other use the same topic. A job, therefore, will have two topics it connects to:

1. A topic that it subscribes to, called the **import_key**
2. A topic that it publishes to, called the **export_key**

In the Application we are running, we will use the following key:

1. **Source Job**:
    - **import_key**: "in-topic". This will simulate an external stream, because we will use the Console Produce to write to this topic
    - **export_key**: "source-job-stream"
2. **Internal Job 1**:
    - **import_key**: "source-job-stream". This is the same topic the Source Job publishes to.
    - **export_key**: "job1-stream"
3. **Sink Job**:
    - **import_key**: "job1-stream"
    - **export_key**: "out-topic". This is the topic our Console Consumer will read from.

This way, we can chain Jobs. The way Kafka is designed, multiple consumers can subscribe to the same topic and streamm it independently, but we won't deal with that (I am still learning parts of the Kafka API).

## Serialization

As I mentioned before, Kafka expects bytes. So we will use a couple different types of Serializers to convert between strings and bytes.

1. **Source Job**:
    - **KafkaStringSerializer**: We will use this to decode the bytes to string
    - **StringSerializer**: This will encode the string to a [MessagePack](https://msgpack.org/) byte payload
2. **Internal Job 1**:
    - **StringSerializer**: This will decode the string from the MessagePack byte payload
    - **StringSerializer**: ibid
3. **Sink Job**:
    - **StringSerializer**: ibid
    - **KafkaStringSerializer**: Encode the string to plain bytes for Kafka.

We are basically testing the following interactions:
- Deserializing a plain bytes message
- Serializing a string to a messagepack byte payload
- Deserializing a messagepack byte payload
- Serializing to a plain bytes message


# Running the Application

## Generating the Jobs
First we'll generate the jobs.

```
cd examples
./generate_job_python.sh kafka-application-example/SourceJob edna_env
./generate_job_python.sh kafka-application-example/InternalJob edna_env
./generate_job_python.sh kafka-application-example/SinkJob edna_env
```

## Running the jobs
We'll run the jobs from inside the `kafka-application-example` directory. We'll first create a namespace for separation of concerns as well.

```
kubectl create namespace kafka-simple-application
kubectl apply -f SourceJob/deployment.yaml -n kafka-simple-application
kubectl apply -f InternalJob/deployment.yaml -n kafka-simple-application
kubectl apply -f SinkJob/deployment.yaml -n kafka-simple-application
```

## Testing the jobs
Start a Console Producer and Console Consumer on separate terminals:

Start the Console Producer with:

```
kubectl -n default run kafka-producer -ti --image=strimzi/kafka:0.19.0-kafka-2.5.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --broker-list edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic in-topic
```

Start the Console Consumer with:

```
kubectl -n default run kafka-consumer -ti --image=strimzi/kafka:0.19.0-kafka-2.5.0 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic out-topic --from-beginning
```

Now, whatever you type in the Console Producer will appear in the Console Consumer after traversing through the Application.