#!/bin/bash

port=$1
n=$2

for (( i=0; i<$n; i++ ))
do
	python master_client.py $port &
	port=$(($port + 1))
done
