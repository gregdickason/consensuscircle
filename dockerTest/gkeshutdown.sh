#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
else
echo WARNING: no clusten name provided. will use previous config
gcloud container clusters get-credentials --zone australia-southeast1-b $1
fi

echo WARNING: This script assumes you have launched on GKE if you have not then you will receive errors

kubectl delete service client redis api
kubectl delete deployment client api
kubectl delete statefulset redis
