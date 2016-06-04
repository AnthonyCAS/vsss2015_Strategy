#!/bin/bash


DIR=`dirname $0`

# Copy config
cp $DIR/data/go_to_from_with_angle.config ~/.vsss_simulator/config.json

vsss_simulator &
sleep 0.5s
python $DIR/../go_to_from_with_angle.py &

# Kill all processes on exit
trap 'kill -- -$$' SIGINT SIGTERM EXIT
wait