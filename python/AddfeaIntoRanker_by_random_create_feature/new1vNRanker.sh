#!/usr/bin/bash

#while(true); do

for i in {0..49}
do
    echo $i
    nohup python -u new1vNRanker.py 2>&1 1>1vNRankerLog/1vNRanker_$i.log &
done

#sleep 600
#done
