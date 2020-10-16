#!/bin/bash

BASE_DIR=$(pwd)

#Run as: ./stress_system.sh [benchmarks] [paths_to_benchmarks_cmd_files]

#refrate
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 508.namd_r 510.parest_r 511.povray_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 527.cam4_r 531.deepsjeng_r 538.imagick_r 541.leela_r 544.nab_r 548.exchange2_r 549.fotonik3d_r 554.roms_r 557.xz_r"

#Important benchmarks
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 531.deepsjeng_r 538.imagick_r 549.fotonik3d_r 554.roms_r 557.xz_r 600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 628.pop2_s 631.deepsjeng_s 649.fotonik3d_s 654.roms_s 657.xz_s"

#refspeed
#bench_list="600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 625.x264_s 627.cam4_s 628.pop2_s 631.deepsjeng_s 638.imagick_s 641.leela_s 644.nab_s 648.exchange2_s 649.fotonik3d_s 654.roms_s 657.xz_s"

#all
#bench_list="500.perlbench_r 502.gcc_r 503.bwaves_r 505.mcf_r 507.cactuBSSN_r 508.namd_r 510.parest_r 511.povray_r 519.lbm_r 520.omnetpp_r 521.wrf_r 523.xalancbmk_r 525.x264_r 526.blender_r 527.cam4_r 531.deepsjeng_r 538.imagick_r 541.leela_r 544.nab_r 548.exchange2_r 549.fotonik3d_r 554.roms_r 557.xz_r 600.perlbench_s 602.gcc_s 603.bwaves_s 605.mcf_s 607.cactuBSSN_s 619.lbm_s 620.omnetpp_s 621.wrf_s 623.xalancbmk_s 625.x264_s 627.cam4_s 628.pop2_s 631.deepsjeng_s 638.imagick_s 641.leela_s 644.nab_s 648.exchange2_s 649.fotonik3d_s 654.roms_s 657.xz_s"

# Input sets to run
# input_list="test train ref"

# For experiments
bench_list=()
cmd_files_list=()
input_list="ref"
	
conf_arr=("-m 0 -N 0" "-m 1 -N 1" "-m 2 -N 2" "-m 3 -N 3")
#conf_arr=("-i 0,1 -N 0" "-i 0,1 -N 1" "-i 2,3 2 -N 2" "-i 2,3 -N 3")


#conf_arr=("-m 0 -N 0" "-m 1 -N 0" "-i 0,1 -N 0")

##############################################################################
# Start stress-ng at the background
# numactl -m 0 -N 0 /home/users/vkarakos/tools/stress-ng/stress-ng --stream 1 &
# sleep 2
##############################################################################

#Counter of benchmarks
cnt=0
#Counter of conf_arr
conf=0
#Input
input="ref"

for bench in $bench_list; do
	echo "--------------------------------------------------------------------------------"
	echo "Executing benchmark: $bench"
	conf=$((cnt/8))	  
	cd $bench/$input
	file=${cmd_files_list[$cnt]}
	echo file: $file
	cmd=$(cat $file)
	cmd=${cmd/base/base.dunnington-x86-m64}
	echo Running with cmd: $cmd
	echo Configuration: ${conf_arr[$conf]}
	(numactl ${conf_arr[$conf]} /bin/bash -c "$cmd") &
	cd ${BASE_DIR}
	cnt=$((cnt+1))
done
echo "Terminating shell script..."

###################################################################
# Stop stress-ng from running at the background
# killall stress-ng
###################################################################

