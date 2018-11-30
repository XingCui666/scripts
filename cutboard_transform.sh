#!/bin/bash

awk '{
split($1,a,"/");
split(a[5],b,".");
filename=b[1]".txt";
if(NF==1){
  printf "" > filename
}
else{
    for(i=0;i<(NF-1)/6;i++)
    {
       confidence=$(i*6+3)
       x=$(i*6+4)
       y=$(i*6+5)
       width=$(i*6+6)-$(i*6+4)
       height=$(i*6+7)-$(i*6+5)
       printf ("%d %d %d %d %.6f\n",x,y,width,height,confidence) >filename
     }
}
close(filename)
}' carface_0.55.list
