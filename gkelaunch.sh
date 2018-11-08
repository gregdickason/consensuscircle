#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
exit 1
fi

gcloud container clusters get-credentials $1
kubectl create -f buildScripts/redis-deployment.yaml
kubectl create -f buildScripts/redis-service.yaml
kubectl create -f buildScripts/rq-worker-deployment.yaml
kubectl create -f buildScripts/rq-worker-service.yaml
kubectl create -f buildScripts/cc-client-deployment.yaml
kubectl expose deployment cc-client --type=LoadBalancer --port 5000 --target-port 5000
