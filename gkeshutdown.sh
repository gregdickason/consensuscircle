#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
else
echo WARNING: no clusten name provided. will use previous config
fi

echo WARNING: This script assumes you have launched on GKE if you have not then you will receive errors

gcloud container clusters get-credentials --zone australia-southeast1-b $1
kubectl delete service cc-client rq-worker redis
kubectl delete deployment cc-client rq-worker
kubectl delete statefulset redis
