#! /bin/sh

if [ "$1" = "" ]
then
	echo "Syntax: ./training.sh datadir"
	exit
fi

dir=$1
traindir=$dir/training
modeldir=$dir/models
for author in $traindir/*
do
	aname=${author:${#traindir}+1}
	python main.py create $modeldir/$aname 5 256
	for doc in $traindir/$aname/*
	do
		python main.py readfile $doc $modeldir/$aname
	done
done
