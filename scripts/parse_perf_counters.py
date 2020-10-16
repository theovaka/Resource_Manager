#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv

# Id of the test correlated with performance counters 
test = sys.argv[1]

path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/"

perf_cnts_path_1 = path_to_results + "test" + test
perf_cnts_path_2 = path_to_results + "test" + test + "_TLB"
perf_cnts_path_3 = path_to_results + "test" + test + "_BW"

results_path = path_to_results + "perf_cnts_t" + test

###########################
#### Save to csv files ####
file_500 = results_path + "/outputs/500s_perf_counters.csv"
file_600 = results_path + "/outputs/600s_perf_counters.csv"

data_500s = []
data_500s.append(["Benchmark", "TT", "IPC", "MPKI", "TLB", "BW"])
data_600s = []
data_600s.append(["Benchmark", "TT", "IPC", "MPKI", "TLB", "BW"])

# List all benchmarks folders inside the  directory
benchmarks = os.listdir(perf_cnts_path_1)
for bench in sorted(benchmarks):
	if (not(bench.startswith('5') or bench.startswith('6'))):
		continue

	if (bench == "511" or bench == "627"):
		continue
	bench_dir = perf_cnts_path_1 + '/' + bench

	# List all output files inside benchmark's directory 
	files = os.listdir(bench_dir)
	for f in sorted(files):

		if (not (("conf_0" in f) and ("ref" in f))):
			continue

		bench_name = f[0:-17]

		fp = open(bench_dir + '/' + f)
		lines = fp.readlines()
		perf_counters = []

		for line in lines:
			tokens = line.split()
			if tokens:
				perf_counters.append(tokens[0])
		
		cycles = int(perf_counters[1])
		instr1 = int(perf_counters[2])
		LLC_load_misses = int(perf_counters[3])
		LLC_store_misses = int(perf_counters[4])
		TT = round(float(perf_counters[5]), 4)

		fp = open(perf_cnts_path_2 + '/' + bench + '/' + f)
		lines = fp.readlines()

		for line in lines:
			tokens = line.split()
			if tokens:
				perf_counters.append(tokens[0])

		instr2 = int(perf_counters[7])
		dTLB_load_misses = int(perf_counters[8])
		dTLB_store_misses = int(perf_counters[9])
		iTLB_load_misses = int(perf_counters[10])
		time_ = float(perf_counters[-1])

		fp = open(perf_cnts_path_3 + '/' + bench + '/' + f)
		lines = fp.readlines()

		for line in lines:
			tokens = line.split()
			if line.startswith("|-- NODE 0 Memory"):
				node_0 = float(tokens[5])
				node_1 = float(tokens[11])
			if line.startswith("|-- NODE 2 Memory"):
				node_2 = float(tokens[5])
				node_3 = float(tokens[11])

		IPC = round(instr1 / cycles, 4)
		MPKI = round((LLC_store_misses + LLC_load_misses) / instr1 * 1000, 4)
		TLB = round((dTLB_store_misses + dTLB_load_misses + iTLB_load_misses) / instr2 * 1000, 4)
		BW = round(node_0 + node_1 + node_2 + node_3, 4)

		if (int(bench) < 600):
			data_500s.append([bench_name, TT, IPC, MPKI, TLB, BW])
		else:
			data_600s.append([bench_name, TT, IPC, MPKI, TLB, BW])


with open(file_500, mode='w') as fl_500:
	file_writer = csv.writer(fl_500, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	file_writer.writerows(data_500s)

with open(file_600, mode='w') as fl_600:
	file_writer = csv.writer(fl_600, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	file_writer.writerows(data_600s)
