#! /bin/sh
for file in fedpapers/testing/*
do
	./crossentropy.sh fedpapers $file
done
