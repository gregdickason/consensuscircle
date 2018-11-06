#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
exit 1
fi

echo INFO: This script assumes you have launched on GKE if you have not then you will receive errors

gcloud container clusters get-credentials $1
kubectl delete service cc-client
kubectl delete deployment cc-client
kubectl delete service rq-worker
kubectl delete deployment rq-worker
kubectl delete service redis
kubectl delete deployment redis
