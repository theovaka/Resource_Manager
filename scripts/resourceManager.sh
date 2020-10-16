#!/bin/bash
BASE_DIR=$(pwd)


declare -a PIDs_arr
# Fetch PIDs of running processes
cd /various/diplom/thvak/spec-2017
for file in *bench_names*; do
	while read line; do
		#echo $line;
		PIDS=$(pidof $line)		
		#echo $PIDS
		for pid in $PIDS
		do
			echo $pid
			PIDs_arr+=($pid)
		done
		# Check for integer
		#if [[ "$PIDS" =~ ^[0-9]+$ ]]
		#then
			#echo $PIDS
		#fi
	done < $file
done
echo "Running processes PIDs..."
echo ${PIDs_arr[@]}
#echo $bench_names
#benchfile= "./500.perlbench_r-cmd-ref-1"
#/bin/bash -c "cat $benchfile"
#while read line;5555
#do
#echo $line
#done < $benchfile

#benchmarks = $(cat $bench_names_file)
#echo $benchmarks
#/bin/bash -c "pidof omnetpp_r_base.dunnington-x86-m64 > ./PIDs.txt"
