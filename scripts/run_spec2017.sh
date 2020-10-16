#!/bin/bash

BASE_DIR=$(pwd)

export GOMP_CPU_AFFINITY="6"
#export OMP_NUM_THREADS=4

#refrate
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 508.namd_r 510.parest_r 511.povray_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 527.cam4_r 531.deepsjeng_r 538.imagick_r 541.leela_r 544.nab_r 548.exchange2_r 549.fotonik3d_r 554.roms_r 557.xz_r"

#Important benchmarks
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 531.deepsjeng_r 538.imagick_r 549.fotonik3d_r 554.roms_r 557.xz_r 600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 628.pop2_s 631.deepsjeng_s 649.fotonik3d_s 654.roms_s 657.xz_s"

#refspeed
#bench_list="600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 625.x264_s 627.cam4_s 628.pop2_s 631.deepsjeng_s 638.imagick_s 641.leela_s 644.nab_s 648.exchange2_s 649.fotonik3d_s 654.roms_s 657.xz_s"

#all
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 508.namd_r 510.parest_r 511.povray_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 527.cam4_r 531.deepsjeng_r 538.imagick_r 541.leela_r 544.nab_r 548.exchange2_r 549.fotonik3d_r 554.roms_r 557.xz_r 600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 625.x264_s 627.cam4_s 628.pop2_s 631.deepsjeng_s 638.imagick_s 641.leela_s 644.nab_s 648.exchange2_s 649.fotonik3d_s 654.roms_s 657.xz_s"

# Id of the test you want to perform
test_id=4

# Input sets to run
# input_list="test train ref"

# For experiments
bench_list="520.omnetpp_r"
input_list="test"
conf_arr=("-i 0,1 -N 0")

#conf_arr=("-m 0 -N 0" "-m 1 -N 0" "-i 0,1 -N 0")

##############################################################################
# Start stress-ng at the background
# numactl -m 0 -N 0 /home/users/vkarakos/tools/stress-ng/stress-ng --stream 1 &
# sleep 2
##############################################################################

for bench in $bench_list; do
    echo "--------------------------------------------------------------------------------"
    echo "Executing benchmark: $bench"
    for input in $input_list; do
        echo "input: $input"    
        #cd $i/test
        #cd $i/train
        #cd $i/ref
        cd $bench/$input
	# Counter for different cmds of same bench and conf
	j=0
        for file in *-cmd-*; do
            #if [ $j -eq 0 ];
	    #then
		#j=$((j+1))
		#continue
	    #fi
	    #if [ $j -eq 1 ];
	    #then
		#j=$((j+1))
		#continue
	    #fi
	    #if [ $j -eq 2 ];
	    #then
		#j=$((j+1))
		#continue
	    #fi
	    echo $file
	    cmd=$(cat $file)
	    cmd=${cmd/base/base.dunnington-x86-m64}
	    echo Running with cmd: $cmd
	    len=${#conf_arr[@]}
	    start=0

	    #############################################
	    # Local conf not included for this experiment
	    # start=1
	    #############################################

	    for (( i=$start; i<$len; i++ )); do
		echo "****************************"
		echo Configuration: ${conf_arr[$i]}
		#(/home/users/vkarakos/tools/IntelPerformanceCounterMonitor-V2.11/pcm-memory.x -csv=../../../results/test1_BW/$(echo $bench | cut -c1-3)/${bench}_${input}_${j}_conf_${i}.out 2>&1 -- numactl ${conf_arr[$i]} /bin/bash -c "$cmd")

		# **** Command for BW experiments ****		
		#(/home/users/vkarakos/tools/IntelPerformanceCounterMonitor-V2.11/pcm-memory.x -- numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/test1_BW/$(echo $bench | cut -c1-3)/${bench}_${input}_${j}_conf_${i}.out 2>&1

		# **** Command for stress effect ****
		#(perf_3.16 stat -e cycles,instructions,LLC-load-misses,LLC-store-misses,dTLB-load-misses,dTLB-store-misses,iTLB-load-misses numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/stress_effect_2_4/${bench}_conf_${i}_stress_8.out 2>&1
		#(perf_3.16 stat -e cycles,instructions,LLC-load-misses,LLC-store-misses,dTLB-load-misses,dTLB-store-misses,iTLB-load-misses numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/test${test_id}/$(echo $bench | cut -c1-3)/${bench}_${input}_${j}_conf_${i}.out 2>&1

		# **** Command for perf counters ****
		#(perf_3.16 stat -e instructions,dTLB-load-misses,dTLB-store-misses,iTLB-load-misses numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/test${test_id}/$(echo $bench | cut -c1-3)/${bench}_${input}_${j}_conf_${i}.out 2>&1
		#time numactl ${conf_arr[$i]} /bin/bash -c "$cmd" #> ../../../results/${bench}_${input}_${i}_time.txt

		# **** Command for thread experiments ****
		(perf_3.16 stat -e cycles,instructions numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/Extra/experimental/${bench}_${input}_${j}_conf_${i}_1_.out 2>&1
		perf_pid=$!		
		# pid=$$
		# echo $pid
		wait $perf_pid

		# **** Command for broady experiments ****
		#(perf_3.16 stat -e instructions,dTLB-load-misses,dTLB-store-misses,iTLB-load-misses numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/Broady/test${test_id}/$(echo $bench | cut -c1-3)/${bench}_${input}_${j}_conf_${i}.out 2>&1
		#(perf_3.16 stat -e cycles,instructions,dTLB-load-misses,dTLB-store-misses,iTLB-load-misses numactl ${conf_arr[$i]} /bin/bash -c "$cmd") > ../../../results/Extra/test3/${bench}_${input}_${j}_conf_${i}.out 2>&1
		#time numactl ${conf_arr[$i]} /bin/bash -c "$cmd" #> ../../../results/${bench}_${input}_${i}_time.txt
	    done
            #uncomment next line when running in dunnington
            #cmd=${cmd/base/base.dunnington-x86-m64}
	    #/bin/bash -c "$cmd"
	    j=$((j+1))
        done
        cd ${BASE_DIR}
    done
done

###################################################################
# Stop stress-ng from running at the background
# killall stress-ng
###################################################################
