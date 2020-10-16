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
	bench_list = []
	IPC_list = []
	MPKI_list =[]
	TLB_list = []
	fp = open(perf_counters_file)
	lines = fp.readlines()
	for line in lines:
		if line.startswith("Benchmark"):
			continue
		tokens = line.split('\t')
		bench_list.append(int(tokens[0]))
		IPC_list.append(float(tokens[1]))
		MPKI_list.append(float(tokens[2]))
		TLB_list.append(float(tokens[3]))

	if ("500" in series):
		res = outputs_path + "/500s_ref_rel.csv"
	else:
		res = outputs_path + "/600s_ref_rel.csv"

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

	confs = ["Remote", "Interleave"]
	for conf in confs:
		fig = plt.figure(figsize=(30,15))
		ax = fig.add_subplot(111)
		ind = np.arange(len(bench_list))
		ax.set_xticks(ind)
		ax.set_xticklabels(bench_list)

		if conf == "Remote":
			temp = remote
		else:
			temp = interleave

		# Calculate prediction based on perf counters and best function
		predicted = []
		for i in range(0, len(bench_list)):
			p = 100
			predicted.append(p + IPC_list[i])

		real = plt.scatter(ind, temp, color='r', marker='o', s=200)
		pred = plt.scatter(ind, predicted, color='g', marker='o', s=200)
		plt.xlabel(conf, fontsize=25)
		plt.ylabel("Permormance 100%", fontsize=25)
		plt.title("Test " + test + " - " + series[:4], fontsize=30)
		plt.grid()
		plt.legend((real, pred), ("Real", "Predicted"), scatterpoints=1, fontsize=25)
		fig_path = plots_path + series[:4] + "_RvsP_" + conf + ".png"
		plt.savefig(fig_path)