#while(true); do

#ps -ef | grep add_feature | awk '{print $2}' | xargs kill -9
for i in {0..49}
do
    echo $i
    nohup python -u newAddFeature.py  ./feature/feature_$i.txt 2>&1 1>addFeatureLog/feature_$i.log &
done

#sleep 600
#done
