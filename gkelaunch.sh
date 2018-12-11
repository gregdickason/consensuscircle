#!/bin/sh

if [ -z "$1" ]
then
echo ERROR: provide name of GKE cluster as argument
echo format: ./GKElaunch.sh <cluster name> <branch name>
exit 1
fi

if [ -z "$2" ]
then
echo ERROR: provide name of GKE cluster as argument
echo format: ./GKElaunch.sh <cluster name> <branch name>
exit 1
fi

gcloud container clusters get-credentials --zone australia-southeast1-b $1

if [ "$2"="master" ]
then
echo CAUTION: launching DEPLOYMENT image
kubectl create -f buildScripts/GKElaunch.yaml
elif ["$2"="cam"]
then
echo CAUTION: launching CAM image
kubectl create -f buildScripts/GKElaunch-cam.yaml
elif ["$2"="greg"]
then
echo CAUTION: launching GREG image
kubectl create -f buildScripts/GKElaunch-greg.yaml
fi
