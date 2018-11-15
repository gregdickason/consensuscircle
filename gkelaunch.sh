#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
exit 1
fi

gcloud container clusters get-credentials --zone australia-southeast1-b $1

if [ -z "$2" ]
then
echo CAUTION: launching DEPLOYMENT image
kubectl create -f buildScripts/GKElaunch.yaml
else
echo CAUTION: launching TEST image
kubectl create -f buildScripts/GKElaunch-test.yaml
fi
