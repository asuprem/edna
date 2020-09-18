# Setup instructions

These steps will help you set up a development environment for the EBKA framework to run a LITMUS application.

## Environment
<span style="color:red; font-weight:bold">Note: At the moment, I highly recommend you follow the WSL2 steps if you have Windows.</span>

EBKA is designed to run on a kubernetes deployment. At the moment, I have only tested on *nix systems, but since kubernetes is platform independent, EBKA should run on any system.

You can follow the following steps for Mac and Windows:

- Mac: [Tutorial : Getting Started with Kubernetes with Docker on Mac](https://rominirani.com/tutorial-getting-started-with-kubernetes-with-docker-on-mac-7f58467203fd#:~:text=%20Tutorial%20%3A%20Getting%20Started%20with%20Kubernetes%20with,now%20to%20expose%20our%20basic%20Nginx...%20More%20)
- Windows: <span style="font-weight:bold;color:red">Note: Follow WSL2 steps below in `Setting up on Windows`, not the link here.</span> 
    - [Deploy on Kubernetes](https://docs.docker.com/docker-for-windows/kubernetes/)
- *Nix: [How to Install and Configure Kubernetes and Docker on Ubuntu 18.04 LTS](https://www.howtoforge.com/tutorial/how-to-install-kubernetes-on-ubuntu/#:~:text=%20How%20to%20Install%20and%20Configure%20Kubernetes%20and,Nodes%20to%20the%20Kubernetes%20Cluster.%20In...%20More%20)

## Setting up on Windows
I highly recommend following these steps for Windows, instead of the links above.

### Setting up WSL2

1. Install an Ubuntu 18.04 distro from the Windows Store. If you already have an installed 18.04 distro that you are using for other work (i.e. it has installed applications and workflows), you should install an Ubuntu 20.04 distro. 
2. Launch it once to set up username and password
3. Upgrade distro to WSL2:
    - You can upgrade in powershell, where `<Distro>` is the name of the distribution:

        ```
        $ wsl --set-version <Distro> 2
        ```
    - You can get a list of installed distros and their names with:
        ```
        $ wsl -l -v
        ```

4. <strong><span style="font-weight:bold;color:red">Bug fix</span></strong>: There is a bug in wsl2 that makes its virtual machine use up all memory. To fix this, we will need to force WSL2 to use a specific amount of memory. For more details, take a look at [this medium post](https://blog.simonpeterdebbarma.com/2020-04-memory-and-wsl/)

    1. Create a `%UserProfile%\.wslconfig` file
    2. Populate file with the following:
    
        ```
        [wsl2]
        memory=4GB
        swap=0
        localhostForwarding=true
        processors=4        
        ```

5. Launch the WSL2 distro. Run the following 2 lines to create a *nix emulation of systemd for Docker:

    ```
    sudo mkdir /sys/fs/cgroup/systemd
    sudo mount -t cgroup -o none,name=systemd cgroup /sys/fs/cgroup/systemd
    ```

## Installing tools
Now we will install Docker, Kubernetes, and KinD (Kubernetes-in-Docker). 

### Update
First, though, we should update the package repo links:

```
$ sudo apt-get update
$ sudo apt-get upgrade
```

### Installing python
Next, we should install python tools. Make sure `python 3` is installed by checking

```
$ python -V
```

Also, be sure to install `pip` and `virtualenv`

```
$ sudo apt-get install python3-pip
$ pip3 install virtualenv
```

### Install `KinD`

```
$ cd ~
$ curl -Lo ./kind https://github.com/kubernetes-sigs/kind/releases/download/v0.7.0/kind-$(uname)-amd64
$ chmod +x ./kind
$ sudo mv ./kind /usr/local/bin/
```

### Then install `kubectl`

```
$ curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
$ chmod +x ./kubectl
$ sudo mv ./kubectl /usr/local/bin/kubectl
```

### Finally install Docker

```
$ curl -LO "https://download.docker.com/linux/static/stable/x86_64/docker-19.03.12.tgz"
$ tar xzvf docker-19.03.12.tgz
$ sudo mv docker/* /usr/bin/
$ sudo dockerd &
$ sudo docker run hello-world
```

NOTE: you will need to run `sudo dockerd &` each time you start a new wsl2 session after terminating the old session. Just closing the terminal window doesn't **terminate** a session. You can get a list of active sessions in Powershell with 

```
wsl -l -v
```

And you can terminate a running session with:

```
wsl --terminate <Distro>
```

### Get the docker bridge
Get your Docker bridge with `sudo docker network inspect bridge` (You will need the <span style="color:lightblue;font-weight:bold">IPAM.subnet</span> field). If you want to parse the output easier, you can use `jid`:

```
sudo apt-get install jid
sudo docker network inspect bridge | jid
```

For example, mine is `172.18.0.0/16`.


## Testing.
Run the following lines.

Note: You can use the cluster.yaml file provided to launch a cluster. It will create a cluster with 1 control node and 1 worker node.

```
sudo kind create cluster --name kind --config cluster.yaml
sudo kind get clusters
sudo kubectl get nodes

sudo kubectl create deployment hello-node --image=k8s.gcr.io/echoserver:1.4
sudo kubectl get deployments
sudo kubectl get pods
sudo kubectl get events
sudo kubectl config view
sudo kubectl expose deployment hello-node --type=LoadBalancer --port=8080
```

## Install `metallb`
Now we install metallb to allow external connections to the clusters when needed.

```
$ sudo kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.3/manifests/namespace.yaml
$ sudo kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.3/manifests/metallb.yaml
$ sudo kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"
```

Now, when you need an external service to connect to the internal pods/nodes, you will create a metallb configutaration YAML and apply it. The file should have:

```
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 172.18.255.1-172.18.255.250
```

NOTE: replace the subnet with your own from docker bridge (i.e. mine was 172.18)

Then apply it with:

```
$ sudo kubectl apply -f metallbconfig.yaml
```

## Checking if we get a response

Next we get the available services:
```
sudo kubectl get services
```

Copy the external IP and the port, and make a request:

```
curl http://<External-IP>:8080
```

You should get a response. Delete the cluster with:

```
sudo kind delete cluster --name kind
```
