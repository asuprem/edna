# EDNA on Kubernetes

This time, we will run a more complex EDNA job on kubernetes that pulls together the prior steps, plus a few more exciting ones.

## Requirements

1. Twitter API account with a Bearer Token
2. Python 3.7
3. Running Kind cluster with 1 control plane node, 1 worker node, and docker registry (Part 3)
4. Kafka broker on kubernetes (Part 2)
5. Virtual environment (Part 4)

## Setup -- Additional Python packages

There are a few additional packages we need for the next steps. These are independent of EDNA, and so are not present in the EDNA dependencies. Install them with pip:

```
pip install j2cli
```

### j2cli

Jinja2 is a powerful templating engine that allows you to create extensible files. `j2cli` is a Jinja2 templating engine wrapper for the command line. 


## Reviewing the Code

We will work on the `examples/job-examples/TwitterSampledStreamerToKafka` example. Take a look at the code right now in `TwitterSampledStreamerToKafka.py`. It contains an EDNA job with the following specifications:

- Ingest with a TwitterStreamingIngest primitive
- Process with BaseProcess (which is an empty primitive that doesn't do anything)
- Emit with a KafkaEmit primitive that sends results to Kafka

The `ednaconf.yaml` associated with the ~~StreamingContext~~ SimpleStreamingContext has the following important fields:
- `bearer_token`: Put your bearer token here
- `kafka_topic`: The name of the kafka topic to publish to. This will be the same topic that another EDNA job could subscribe to, for example
- `bootstrap_server`: The address of the kafka broker. 
    - You can get it with `kubectl get services -n kafka`. This will return several services for the `kafka` namespace. We want the bootstrap service, plus the full DNS address. 
    - In Kubernetes, the full DNS address of a service is: `<service-name>.<namespace>.svc.cluster.local`. 
    - Resolving this gets us `edna-cluster-kafka-bootstrap.kafka.svc.cluster.local`

### ~~StreamingContext~~ SimpleStreamingContext

First we create the ~~StreamingContext~~ SimpleStreamingContext:

```
context = SimpleStreamingContext()
```

This manages the Edna Job by configuring and executing it. We don't want to hard-code any variables for the job, because this makes management of resources and jobs difficult. Instead, we will always try for configurable jobs. In this case, the configuration is set up by passing variables into the `StreamingContext` through a configuration file. `StreamingContext` loads variables from a local file with the default name `ednaconf.yaml`. A top level field called `variables` should contain all Context variables we want to pass. 

### Serializers 

We then create two serializers:

```
ingest_serializer = EmptyStringSerializer()
emit_serializer = EmptyStringSerializer()
```

Serialization is an important part of streaming (andany networking). Serialization is technically two tasks:
- Serialization: convert an object to bytes
- Deserialization: recover an object from bytes

Twitter provides a stream of newline-separated strings. So our `ingest_serializer` does not need to do anything, because we already get a string directly from Twitter.

We do need an emit serializer, though, since we want our emitter to send the information to Kafka, which expects bytes. ~~Since our internal representation is a String, we will use a StringSerializer.~~<span style="color:maroon">This has been updated to EmptyStringSerializer, since Twitter now provides bytes as its message payload, so we don't need to do anything to encode the message.</span>

If you look inside `edna.emit.BaseEmit` class, you will see that the `__call__` method is:

```
def __call__(self, message):
    self.write(self.serializer.write(message))
```

So any Emit primitive, when called to emit a message, will call its own `write()` method after serializing the message.

### Setting up primitives

Next we set up the ingest, process, and emit primitives. We will pass in the serializers plus the context variables stored in the `StreamingContext` with `getVariable()`. 

```
ingest = TwitterStreamingIngest(serializer=ingest_serializer, 
    bearer_token=context.getVariable("bearer_token"), 
    tweet_fields=context.getVariable("tweet_fields"), 
    user_fields=context.getVariable("user_fields"), 
    place_fields=context.getVariable("place_fields"), 
    media_fields=context.getVariable("media_fields"))
process = BaseProcess()
emit = KafkaEmit(serializer=emit_serializer, 
    kafka_topic=context.getVariable("kafka_topic"), 
    bootstrap_server=context.getVariable("bootstrap_server"),
    bootstrap_port=context.getVariable("bootstrap_port"))
```

### Adding primitives

We then add the primitives to the `StreamingContext`:

```
context.addIngest(ingest)
context.addProcess(process)
context.addEmit(emit)
```

###  Execution

Finally, we execute the context with:

```
context.execute()
```

which, in turn, calls the `run()` method of `StreamingContext()`:

```
for streaming_item in self.ingest:  # This calls __next__
    self.emit(self.process(streaming_item))
```

# Running the Job

Now, let's run the Job on Kubernetes. The overall plan is as follows:

1. Create a docker image that contains the job plus any dependencies
2. Deploy docker image to registry
3. Create a podspec that will pull the image from registry and launch a pod
4. Verify pod works by reading the kafka stream

## Ensuring environment

Before we do that, we should make sure our environment is set up properly.

You can use the steps in earlier parts for this, i.e. testing kafka with brokers and testing the registry with a simple pull and run of a docker image.

## Creating the docker image

### Dockerfile generation

There is a naive way to create the docker image: simple use the python base docker image, add the file and the EDNA library with a Dockerfile. Unfortunately, this will create a Docker image that is at least 900MB. This is because the base python library includes a lot of unnecessary files and libraries, plus development copies of python. 

So we will use something called a multistage docker file. We will start with the `python3.7-slim` image from dockerhub. This is much smaller than the base python image. We will use this image to compile our job file (`TwitterSampledStreamToKafka.py`) into a C program. This will significantly reduce the dependencies we require, plus make our program faster since we are compiling to C. Then we will copy the compiled C file to a fresh image that has no installation debris, so to speak.

Take a look at `Dockerfile.jinja2` in `examples`. It has enough comments to explain what is going on.

Since it is a **jinja2** file, it has some template variables in there, such as `{{ template.filename }}`. This allows us to use this Dockerfile for different types of jobs by creating a compilation configuration file.

Now go back inside the `TwitterSampledStreamerToKafka` directory. There is a `config.yaml` file in there. For future jobs, you will edit this. The variables here will be passed by **Jinja2** into the template Dockerfile. So, *TwitterSampledStreamerToKafka* will replace any instances of `{{  template.filename }}` in the `Dockerfile.jinja2`.

Inside the `TwitterSampledStreamerToKafka` directory, create the Dockerfile through Jinja2 with:

```
j2 /path/to/repo/examples/Dockerfile.jinja2 config.yaml > Dockerfile
```

Take a look at the generated Dockerfile. It should have replaced the template with the correct names

### Preparing the directory.

Before creating the image, we still need to make sure it can add the EDNA library. Unfortunately, we will be working within this directory and docker's safety features prevent it from accessing files above the current directory.

So, copy the edna python library (I have provided relative paths below that should work):

```
cp -r /path/to/repo/python/edna/src .
cp /path/to/repo/python/edna/setup.py .
cp /path/to/repo/python/edna/setup.cfg .
```

**Note** Make sure you added your bearer-token to the `ednaconf.yaml` file.

### Generate the dockerignore

Use the following command to generate the dockerignore if it does not exist:

```
cat <<EOF > .dockerignore
# Ignore .git and .cache
.git
.cache

# Ignore config yaml files and generated docker.sh file
config.yaml
deployment.yaml
docker.sh
EOF
```

### Build the image

I am going to choose the name `edna-twitter-kafka` as the name for the image. Build the image with:

```
docker build -t edna-twitter-kafka:latest .
```

Then push to the registry with:

```
docker tag edna-twitter-kafka:latest localhost:5000/edna-twitter-kafka:latest
docker push localhost:5000/edna-twitter-kafka:latest
```

You can check whether the push worked by using `joxit` image or with the registry API (see the Docker Registry Setup instructions). You can also check the image size with:

```
docker image ls
```

It should be 141MB, which is still fairly large. There are ways to make it even smaller, but we won't go into that.

## Running the Job

Next, we will run the job. The `deployment.yaml` sets it up. Keep note of the following:

- `replicas: 1` : We want a  a single pod
- `name: twitter-kafka`: Sets the name of the pod
- `image: localhost:5000/edna-twitter-kafka:latest`: Sets the image of the pod

If you are working on Custom Resources these configurations are useful things to add to a custom resource (along with the template `config.yaml` for the Dockerfile) -- this way, you can automate the overall process.


### Preparing

Before running the job, launch a second terminal and set it up to receive a kafka feed. That way when the Job begins running, you will directly get the stream from kafka.

```
kubectl -n default run kafka-consumer -ti --image=strimzi/kafka:0.19.0-kafka-2.5.0 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic twitter-sampled-stream --from-beginning
```

Note the topic -- I use the same topic that the Job is using to publish the stream.

When you run this, you might get some LEADER_MISSING or similar messages. You can ignore them.

### Running the job

Now apply the Job with:

```
kubectl apply -f deployment.yaml
```

You should get a stream on your second terminal in a bit.

Kill the pod with 

```
kubectl delete -f deployment.yaml
```

The stream will end after a bit (it might take a while to end since it is still working on clearing its buffer).

You can exit the kafka terminal eith `Ctrl-C`.









