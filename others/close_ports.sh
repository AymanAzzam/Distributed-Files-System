#!/bin/bash

if (( $(ps -eo comm,pid,etimes | awk '/^ZMQbg/ { print $2}' | wc -l) > 0 ))
then
	kill -9 $(ps -eo comm,pid,etimes | awk '/^ZMQbg/ { print $2}')
fi
