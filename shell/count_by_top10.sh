#!/bin/bash
for((i=0;i<30;i++))
do
	awk '
	BEGIN{cnt=0}
	{if($3==0 && $4>0.7+i/100) cnt++}
	END{print "score>"0.7+i/100,"\t",cnt}
	' i=$i toplist_2w.file.1822
done
