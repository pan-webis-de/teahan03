#! /bin/sh

if [ "$1" = "" ] || [ "$2" = "" ]
then
	echo "Syntax: ./crossentropy.sh datadir testfile"
	exit
fi
dir=$1
modeldir=$dir/models
testfile=$2

echo "cross-entropy of $testfile..."
echo ""
for model in $modeldir/*
do
	echo "${model:${#modeldir}+1}:"
	python main.py crossentropy $testfile $model
	echo ""
done
