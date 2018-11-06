#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
exit 1
fi

gcloud container clusters get-credentials $1
kubectl create -f deploymentScripts/redis-deployment.yaml
kubectl create -f deploymentScripts/redis-service.yaml
kubectl create -f deploymentScripts/rq-worker-deployment.yaml
kubectl create -f deploymentScripts/rq-worker-service.yaml
kubectl create -f deploymentScripts/cc-client-deployment.yaml
kubectl expose deployment cc-client --type=LoadBalancer --port 5000 --target-port 5000
