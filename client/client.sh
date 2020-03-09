#!/bin/bash

port=$1
n_master=$2
n_clients=$3

for (( i=0; i<$n_clients; i++ ))
do
	python client.py $port $n_master $i &
done
