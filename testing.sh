#! /bin/sh

if [ "$1" = "" ]
then
	echo "Syntax: ./testing.sh datadir"
	exit
fi

dir=$1
testdir=$dir/testing
modeldir=$dir/models


for testauthor in $testdir/*
do

	for testfile in $testauthor/*
	do
		min=1000
		author=""
		equal=0
		echo "testing $testfile..."
		for model in $modeldir/*
		do
			c=$(python main.py crossentropy $testfile $model)
			if [ "$c" = "$min" ]
			then
				equal=1
			fi
			if [ 1 -eq "$(echo "${c} < ${min}" | bc)" ]
			then
				min=$c
				author=$model
			fi
		done
		if [ "${author:${#modeldir}+1}" == "${testauthor:${#testdir}+1}" ]
		then
			echo "pass!"
		else
			echo "fail!"
			echo $testfile >> $dir/fail.txt
		fi
		if [ $equal -eq 1 ]
		then
			echo "equalities found..."
			echo $testfile >> $dir/equal.txt
		fi
	done

done
