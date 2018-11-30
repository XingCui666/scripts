#!/bin/bash
for name in path/*
do
	echo $name
	let i+=1
	new=$i
	echo $new
	mv $name path/"abc"_$new.jpg
done
