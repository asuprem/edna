# Setting up and testing Kafka on Kubernetes

## Apache Kafka
Kafka is an open-source distributed event streaming platform...you are probably better off reading the [wikipedia article](https://en.wikipedia.org/wiki/Apache_Kafka) and the [apache kafka page](https://kafka.apache.org/).

In any case, Kafka is highly durable, fast, and operates as a pub/sub interface. This makes it perfect for streaming, and it's used essentially everywhere.

## Setting up

### Cluster
First create a cluster if you have not done so already. You can use the same `cluster.yaml` from Part 1, also provided here.

```
sudo kind create cluster --name kind --config cluster.yaml
```

### Namespace
Then we create a namespace for kafka.

```
kubectl create namespace kafka
```

### Controller
Next, we apply a kafka controller that will manage kafka resources. This is an example of a Kubernetes Custom Resource and Custom Resource Controller.

```
kubectl apply -f kafka-operator.yaml -n kafka
```

You can get the operator from [Strimzi]('https://strimzi.io/') with the following code, but I have provided it for you here as well in `kafka-operator.yaml`

```
wget https://strimzi.io/install/latest?namespace=kafka
```

### Watching the deployment

You can watch the operator get deployed with the following code, which will automatically update each time the operator's container enters a new phase (i.e. ContainerCreating, Ready, NotReady, etc). It's not that interesting.

```
kubectl get pod -n kafka --watch
```

You can also get a log of events (a bit more interesting, imo) for the operator with the following code. Since the operator is fairly complex and needs to download a few images, this might take a while, so don't get frustrated if you have a blank screen for ~5 min.

```
kubectl logs deployment/strimzi-cluster-operator -n kafka -f
```

## Launching Kafka brokers
Once we have the operator, we can launch Kafka brokers that actually handle the streaming events

You can get the configuration of brokers with the following line, but I recommend using the `kafka-persistent-single.yaml` I have provided, since I have made some useful configuration changes.

```
curl -LO https://strimzi.io/examples/latest/kafka/kafka-persistent-single.yaml
```

If you do choose to download, you should do the following:
    - change resource requests for the `persistent-claim` from  `100Gi` to `5Gi`
    - change `name` from `my-cluster` to `edna-cluster`

Apply it with:

```
sudo kubectl apply -f kafka-persistent-single.yaml -n kafka
```

You can get a notification for when it is ready with:
```
sudo kubectl wait kafka/edna-cluster --for=condition=Ready --timeout=300s -n kafka 
```

This will timeout in 5 min, so if it takes longer, just rerun the command, or run it with a longer timeout.

## Testing kafka
You should open two terminals. You will use `Terminal 1` to send messages to kafka under a particular topic. `Terminal 2` will subscribe to that topic and pull any messages as and when the are published to the topic from `Terminal 1` (basically a glorified one-way chat).

### Terminal 1
First run:

```
sudo kubectl -n default run kafka-producer -ti --image=strimzi/kafka:0.19.0-kafka-2.5.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --broker-list edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic my-topic
```

Wait a few moments for it to launch. Now you can enter messages. The first message you enter might show an error about a "missing Leader" but this will likely be automatically fixed in the backend by the controller.

Now you can write messages. But first...

### Terminal 2
In this terminal, run

```
sudo kubectl -n default run kafka-consumer -ti --image=strimzi/kafka:0.19.0-kafka-2.5.0 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092 --topic my-topic --from-beginning
```

This will start the subscriber. Now back on `Terminal 1`, any message you type should appear on `Terminal 2`

### Dissection
Let's analyze the two lines to learn more about what they are doing.

- `sudo kubectl`: Entry point
- `-n default`: Run it in the default namespace i.e. NOT the kafka namespace where the controller and brokers are. This is just a client.
- `run kafka-producer`: Name for the deployment
- `-ti`: Run this deployment in interactive mode with a terminal attached
- `--image=strimzi/kafka:0.19.0-kafka-2.5.0`: Which image to use for this deployment
- `--rm=true`: This deletes the deployment upon exit
- `--restart=Never`: Make sure the pod dies upon exit
- `-- bin/kafka-console-producer.sh`: What command to run inside the pod
    - `--broker-list edna-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092`: The address for the broker. You can get the address by doing `kubectl get services -n kafka` and taking node of the routing information. It should match this.
    - `--topic my-topic`: What topic to publish to.

The line for the consumer on `Terminal 2` is mostly the same, the sole difference being it launches `kafka-console-consumer.sh` and has a `--from-beginning` flag to tell the consumer to pull all messages under the topic.

## Deleting
Once you are done, delete with:

```
sudo kubectl delete -f kafka-persistent-single.yaml -n kafka
sudo kubectl delete -f kafka-operator.yaml -n kafka
sudo kubectl delete namespace kafka
```

You can delete the cluster with 

```
sudo kind delete cluster --name kind
```