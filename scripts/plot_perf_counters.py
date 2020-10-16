#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv

# Id of the test correlated with the plots to be created
test = sys.argv[1]

path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/"

outputs_path = path_to_results + "test" + test + "/outputs"
plots_path = path_to_results + "test" + test + "/plots/"

perf_counters_path = path_to_results + "perf_cnts_t" + test + "/outputs/"
series_list = ["500s_perf_counters.csv", "600s_perf_counters.csv"]

for series in series_list:
	perf_counters_file = perf_counters_path + series
	IPC_list = []
	MPKI_list =[]
	TLB_list = []
	BW_list = []
	fp = open(perf_counters_file)
	lines = fp.readlines()
	for line in lines:
		if line.startswith("Benchmark"):
			continue
		tokens = line.split('\t')
		IPC_list.append(float(tokens[1]))
		MPKI_list.append(float(tokens[2]))
		TLB_list.append(float(tokens[3]))
		BW_list.append(float(tokens[4]))

	if ("500" in series):
		res = outputs_path + "/500s_ref_abs.csv"
	else:
		res = outputs_path + "/600s_ref_abs.csv"

	fp = open(res)
	lines = fp.readlines()
	local = []
	remote = []
	interleave = []
	for line in lines:
		if line.startswith("Benchmark"):
			continue
		tokens = line.split('\t')
		local.append(100*float(tokens[1]))
		remote.append(100*float(tokens[2]))
		interleave.append(100*float(tokens[3]))

	perf_counters = ["IPC", "MPKI", "TLB", "BW"]
	for perf_cnt in perf_counters:
		fig = plt.figure(figsize=(30,15))
		fig.add_subplot(111)
		if perf_cnt == "IPC":
			temp = IPC_list
		elif perf_cnt == "MPKI":
			temp = MPKI_list
		elif perf_cnt == "TLB":
			temp = TLB_list
		else:
			temp = BW_list
		loc = plt.scatter(temp, local, color='r', marker='o', s=200)
		rem = plt.scatter(temp, remote, color='g', marker='o', s=200)
		inter = plt.scatter(temp, interleave, color='b', marker='o', s=200)
		plt.xlabel(perf_cnt, fontsize=25)
		plt.ylabel("Permormance 100%", fontsize=25)
		plt.title("Test " + test + " - " + series[:4], fontsize=30)
		plt.grid()
		plt.legend((loc, rem, inter), ("Local", "Remote", "Interleave"), scatterpoints=1, fontsize=25)
		fig_path = plots_path + series[:4] + "_" + perf_cnt + ".png"
		plt.savefig(fig_path)

