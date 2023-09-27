# About Exoscale

As the website of [Exoscale](https://www.exoscale.com/) mentions:

!!! quote

    Exoscale is the leading Swiss/European cloud service provider.

    With services covering the full cloud infrastructure spectrum - from fast deploying virtual machines and S3 compatible object storage to a scalable kubernetes service and databases - Exoscale provides a simple and scalable experience in order to let its clients focus on their core business.

## How and why do we use Exoscale

We use Exoscale to deploy and host our platform in a production ready environment.

## Access Exoscale

To access Exoscale Kubernetes cluster, ask a team member.

## Configuration

_None._

## Common tasks

### Install the Exoscale CLI

To install the Exoscale CLI, follow the [official documentation](https://community.exoscale.com/documentation/tools/exoscale-command-line-interface/) for your distribution.

### Configure the Exoscale CLI

To configure the Exoscale CLI, follow the [official documentation](https://community.exoscale.com/documentation/tools/exoscale-command-line-interface/#configuration) to 

### Create a Kubernetes cluster

To create a Kubernetes cluster, the following steps must be followed (based on the [official documentation](https://community.exoscale.com/documentation/sks/quick-start/)).

#### Create a security group

Create the security group for Kubernetes.

```sh
# Create the security group
exo compute security-group create sks-security-group
```

#### Add rules to security group

Add the necessary rules to the security group.

```sh
# 30000 to 32767 TCP from all sources for NodePort and LoadBalancer services
exo compute security-group rule add sks-security-group \
    --description "NodePort services" \
    --protocol tcp \
    --network 0.0.0.0/0 \
    --port 30000-32767

# 10250 TCP with the security group as a source
exo compute security-group rule add sks-security-group \
    --description "SKS kubelet" \
    --protocol tcp \
    --port 10250 \
    --security-group sks-security-group

# 4789 UDP with the security group as a source for VXLAN communication between nodes
exo compute security-group rule add sks-security-group \
    --description "Calico traffic" \
    --protocol udp \
    --port 4789 \
    --security-group sks-security-group
```

#### Initialize the Kubernetes cluster

```sh
# Initialize the Kubernetes cluster
exo compute sks create swiss-ai-center-prod \
    --zone ch-gva-2 \
    --service-level starter \
    --nodepool-name swiss-ai-center-prod-nodepool \
    --nodepool-size 1 \
    --nodepool-instance-type small \
    --nodepool-disk-size 20 \
    --nodepool-security-group sks-security-group
```

!!! tip

    If you ever need to delete the Kubernetes cluster, you can delete it with the followings commands:

    ```sh
    # Delete the Kubernetes cluster nodepool
    exo compute sks nodepool delete swiss-ai-center-prod swiss-ai-center-prod-nodepool

    # Delete the Kubernetes cluster itself
    exo compute sks delete swiss-ai-center-prod
    ```

### Generate the kubeconfig file

Generate the Kubernetes configuration file to use with [kubectl]().

```sh
exo compute sks kubeconfig swiss-ai-center-prod kube-admin \
    --zone ch-gva-2 \
    --group system:masters > swiss-ai-center-prod.kubeconfig
```

### Access the Kubernetes cluster with the kubectl file

To validate kubectl can access the Kubernetes cluster, you can check if it can get the nodes.

```sh
# Get the nodes
kubectl --kubeconfig swiss-ai-center-prod.kubeconfig get node
```

The output should be similar to this.

```
NAME               STATUS   ROLES    AGE   VERSION
pool-d5c11-ltbap   Ready    <none>   14m   v1.27.3
```

### Deploy ingress-nginx controller to use domain names

In order to deploy Kubernetes pods with a domain name, an Ingress controller must be deployed.

It will be used as a reverse proxy to redirect the traffic to the correct Kubernetes pods.

```sh
# Install the ingress-nginx for Exoscale
kubectl apply \
    --kubeconfig swiss-ai-center-prod.kubeconfig  \
    --filename https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/exoscale/deploy.yaml
```

### Link a domain name to the Kubernetes cluster

To link a domain name to the Kubernetes cluster, the following steps must be followed.

_TODO_

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

_None at the moment._
