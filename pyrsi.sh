#!/bin/bash
sleep 9
cd `dirname "$0"`
while [ 1 ]; do
  nice python3 ./rsi.py &> log
done
