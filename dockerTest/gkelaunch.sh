#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
exit 1
fi

gcloud container clusters get-credentials $1
kubectl create secret generic env-secrets --from-literal=REDIS_PASS=asdf
kubectl create -f redis-deployment_persist.yaml
kubectl create -f client-deployment.yaml
kubectl expose deployment cc-client --type=LoadBalancer --port 4000 --target-port 80
