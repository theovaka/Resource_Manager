#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv

# Directory name of the results to plot 
test = sys.argv[1]
path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/"

results_path_1 = path_to_results + "test1"
results_path_2 = path_to_results + test
 
files = ["500s_ref_abs.csv", "600s_ref_abs.csv"]

# Initialise lists to store results
bench_list = []
loc1_list = []
rem1_list = []
inter1_list = []
loc2_list = []
rem2_list = []
inter2_list =[]

for file in files:
	if (int(test[4])!=2 and int(test[4])!=4):
		file_1 = results_path_1 + "/outputs/" + file
	else:
		file_1 = results_path_1 + "/outputs/" + file[:12] + "_imp.csv"
	file_2 = results_path_2 + "/outputs/" + file
	fp1 = open(file_1)
	fp2 = open(file_2)
	lines1 = fp1.readlines()
	lines2 = fp2.readlines()

	for line1, line2 in zip(lines1, lines2):
		if (line1.startswith("Benchmark") or line2.startswith("Benchmark")):
			continue
		tokens1 = line1.split()
		tokens2 = line2.split()
		bench_list.append(int(tokens1[0]))
		loc1_list.append(float(tokens1[1]))
		rem1_list.append(float(tokens1[2]))
		inter1_list.append(float(tokens1[3]))
		loc2_list.append(float(tokens2[1]))
		rem2_list.append(float(tokens2[2]))
		inter2_list.append(float(tokens2[3]))

 	##########################
	###### Create plots ######

	# Plot for 500 series
	ind = np.arange(len(bench_list))
	width = 0.14
	fig = plt.figure(figsize=(30,15))
	ax = fig.add_subplot(111)
	ax.set_title("SPEC 2017 time stats - test1 vs " + test)

	rects1 = ax.bar(ind, loc1_list, width, color='r')
	rects2 = ax.bar(ind+width, loc2_list, width, color='c')
	rects3 = ax.bar(ind+width*2, rem1_list, width, color='g')
	rects4 = ax.bar(ind+width*3, rem2_list, width, color='m')
	rects5 = ax.bar(ind+width*4, inter1_list, width, color='b')
	rects6 = ax.bar(ind+width*5, inter2_list, width, color='y')

	ax.set_xticks(ind+width*2.5)
	ax.set_xticklabels(bench_list)
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0]), ('Local-test1', 'Local-'+test, 'Remote-test1', 'Remote-'+test, 'Interleave-test1', 'Interleave'+test))

	plot_path = results_path_2 + "/plots/" + file[0:3] + "s_cmp_test1.png"
	plt.savefig(plot_path)
	
	bench_list = []
	loc1_list = []
	rem1_list = []
	inter1_list = []
	loc2_list = []
	rem2_list = []
	inter2_list =[]