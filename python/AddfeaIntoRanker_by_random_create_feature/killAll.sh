#!/bin/bash

ps -ef|grep -iE "oldAddFeature|1vNRanker.py|addFeature.py" |awk '{print $2}'|xargs kill -9
