#!/bin/bash

awk '{
split($1,a,"/");
filename="result_txt/Algorithm_VS_SSD_pf/model2/"a[2]".txt";
if(NF==1)
{
  printf "" > filename
}
else
{
  confidence=$2
  x=$3
  y=$4
  width=$5-$3
  height=$6-$4
  printf ("%d %d %d %d %.6f\n",x,y,width,height,confidence) >>filename
}
close(filename)
}' model2.txt.new
