# Docker Hub Mutator

> Original idea from the #YouWillNeverCodeAlone group.

Kubernetes mutator to change any container image to be downloaded from google mirror instead of downloading directly from Docker Hub.
It should avoid the [new rate limit Docker inc is setting up in its Hub](https://docs.docker.com/docker-hub/download-rate-limit/).

## Disclaimer

This project is a simple **POC**.
It has some pending points to be implemented before consider it a beta software.

- It only mutates deployment objects.
- It only mutates the first container image in a deployment object.
- It only mutates CREATE requests.

## Run it locally

### Requirements

Create a local kind cluster then install cert-manager:

```bash
$ kind create cluster
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.19.1) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Have a nice day! 👋
$ kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v1.0.4/cert-manager.yaml
customresourcedefinition.apiextensions.k8s.io/certificaterequests.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/certificates.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/challenges.acme.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/clusterissuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/issuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/orders.acme.cert-manager.io created
namespace/cert-manager created
serviceaccount/cert-manager-cainjector created
serviceaccount/cert-manager created
serviceaccount/cert-manager-webhook created
clusterrole.rbac.authorization.k8s.io/cert-manager-cainjector created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-issuers created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-clusterissuers created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-certificates created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-orders created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-challenges created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-ingress-shim created
clusterrole.rbac.authorization.k8s.io/cert-manager-view created
clusterrole.rbac.authorization.k8s.io/cert-manager-edit created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-cainjector created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-issuers created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-clusterissuers created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-certificates created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-orders created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-challenges created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-ingress-shim created
role.rbac.authorization.k8s.io/cert-manager-cainjector:leaderelection created
role.rbac.authorization.k8s.io/cert-manager:leaderelection created
role.rbac.authorization.k8s.io/cert-manager-webhook:dynamic-serving created
rolebinding.rbac.authorization.k8s.io/cert-manager-cainjector:leaderelection created
rolebinding.rbac.authorization.k8s.io/cert-manager:leaderelection created
rolebinding.rbac.authorization.k8s.io/cert-manager-webhook:dynamic-serving created
service/cert-manager created
service/cert-manager-webhook created
deployment.apps/cert-manager-cainjector created
deployment.apps/cert-manager created
deployment.apps/cert-manager-webhook created
mutatingwebhookconfiguration.admissionregistration.k8s.io/cert-manager-webhook created
validatingwebhookconfiguration.admissionregistration.k8s.io/cert-manager-webhook created
```

### Build and deploy

Wait until all cert-manager containers are running, then after cloning this repository, run the following commands:

```bash
$ docker build -q --no-cache -t dockerhub-mutator:latest .
sha256:8820d2f24d9e761fff880f554cff11ed587183dee782625a443b3eea7a09df13
$ kind load docker-image dockerhub-mutator:latest
Image: "dockerhub-mutator:latest" with ID "sha256:8820d2f24d9e761fff880f554cff11ed587183dee782625a443b3eea7a09df13" not yet present on node "kind-control-plane", loading...
$ kubectl apply -f hack/deploy.yaml
issuer.cert-manager.io/mutator-root created
certificate.cert-manager.io/mutator-root-ca created
issuer.cert-manager.io/mutator-root-ca created
certificate.cert-manager.io/dockerhub-mutator created
deployment.apps/dockerhub-mutator created
service/dockerhub-mutator created
$ kubectl apply -f hack/mutation.yaml
mutatingwebhookconfiguration.admissionregistration.k8s.io/dockerhub-mutator created
```

### Test it

Once everything is placed, create a deployment

```bash
$ kubectl create deployment example-mutation --image=nginx:latest
deployment.apps/example-mutation created
```

Inspect the deployment:

```bash
$ kubectl get deployment example-mutation -o jsonpath='{.metadata.labels.mutated}'
yes
$ kubectl get deployment example-mutation -o jsonpath='{.spec.template.spec.containers[0].image}'
mirror.gcr.io/library/nginx:latest
```

The image name has been changed. Now it is configured to use the `mirror.gcr.io` google container registry.


## Thanks

Thanks to [@javierprovecho](https://github.com/javierprovecho) to participate in the live coding session at twitch. We built it together!
