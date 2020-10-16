#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv

# Directory name of the results to plot 
test = sys.argv[1]
# Number of different configurations
confs = int(sys.argv[2])
# Local performance counters to be taken from test1 results (True)or from current test results (False)
absolute = True
if (len(sys.argv) > 3):
	if (sys.argv[3] == "rel"):
		absolute = False

path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/"

results_path = path_to_results + test

# dirpath = os.getcwd()
# print("current directory is : " + dirpath)
# foldername = os.path.basename(dirpath)
# print("Directory name is : " + foldername)

inputs = ["test", "train", "ref"]
for input_set in inputs:
	# Initialisations for plots
	p1_x_axis = []
	p1_loc = []
	p1_rem = []
	p1_inter = []

	p2_x_axis = []
	p2_loc = []
	p2_rem = []
	p2_inter = []

	# List all benchmarks folders inside the results directory
	benchmarks = os.listdir(results_path)
	for bench in sorted(benchmarks):
		if (not(bench.startswith('5') or bench.startswith('6'))):
			continue

		if (bench == "511" or bench == "627"):
			continue
		bench_dir = results_path + '/' + bench

		# List all output files inside benchmark's directory 
		files = os.listdir(bench_dir)
		curr = 0
		local=remote=interleave=-1
		for f in sorted(files):

			if (not(input_set in f)):
				continue

			fp = open(bench_dir + '/' + f)
			lines = fp.readlines()
			perf_counters = []

			for line in lines:
				tokens = line.split()
				if tokens:
					perf_counters.append(tokens[0])

			time = float(perf_counters[-1])

			if ((absolute) and (curr == 0)):
				if ("conf_0" in f):
					abs_f = f
				else:
					abs_f = f.replace("conf_1", "conf_0")

				path = path_to_results + "test1/" + bench + "/" + abs_f
				abs_file = open(path)
				lines = abs_file.readlines()
				abs_perf_counters = []

				for line in lines:
					tokens = line.split()
					if tokens:
						abs_perf_counters.append(tokens[0])

				abs_time = float(abs_perf_counters[-1])
				if (confs < 3):
					local = abs_time
					reference = abs_time
					curr = 1


			if (curr == 0):
				if (absolute):
					local = time
					reference = abs_time
				else:
					local = time
					reference = time
			elif (curr == 1):
				remote = time
			else:
				interleave = time
			
			if (curr == 2):
				if (int(bench) < 600):
					p1_x_axis.append(int(bench))
					p1_loc.append(local / reference)
					p1_rem.append(remote / reference)
					p1_inter.append(interleave / reference)
				else:
					p2_x_axis.append(int(bench))
					p2_loc.append(local / reference)
					p2_rem.append(remote / reference)
					p2_inter.append(interleave / reference)
				local=remote=interleave=-1
			curr = (curr + 1) % 3

	###########################
	#### Save to csv files ####
	if (absolute):
		file_500 = results_path + "/outputs/500s_" + input_set + "_abs.csv"
		file_600 = results_path + "/outputs/600s_" + input_set + "_abs.csv"
		file_all = results_path + "/outputs/all_" + input_set + "_abs.csv"
	else:
		file_500 = results_path + "/outputs/500s_" + input_set + "_rel.csv"
		file_600 = results_path + "/outputs/600s_" + input_set + "_rel.csv"
		file_all = results_path + "/outputs/all_" + input_set + "_rel.csv"

	data_all = []
	data_all.append(["Benchmark", "Local", "Remote", "Interleave"])

	data_500s = []
	data_500s.append(["Benchmark", "Local", "Remote", "Interleave"])
	for i in range (len(p1_x_axis)):
		data_500s.append([p1_x_axis[i], p1_loc[i], p1_rem[i], p1_inter[i]])
		data_all.append([p1_x_axis[i], round(100*p1_loc[i], 4), round(100*p1_rem[i], 4), round(100*p1_inter[i], 4)])

	data_600s = []
	data_600s.append(["Benchmark", "Local", "Remote", "Interleave"])
	for i in range (len(p2_x_axis)):
		data_600s.append([p2_x_axis[i], p2_loc[i], p2_rem[i], p2_inter[i]])
		data_all.append([p2_x_axis[i], round(100*p2_loc[i], 4),round(100*p2_rem[i], 4), round(100*p2_inter[i], 4)])

	with open(file_500, mode='w') as fl_500:
		file_writer = csv.writer(fl_500, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		file_writer.writerows(data_500s)

	with open(file_600, mode='w') as fl_600:
		file_writer = csv.writer(fl_600, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		file_writer.writerows(data_600s)

	with open(file_all, mode='w') as fl_all:
		file_writer = csv.writer(fl_all, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		file_writer.writerows(data_all)

	##########################
	###### Create plots ######

	# Plot for 500 series
	ind = np.arange(len(p1_x_axis))
	width = 0.27
	fig = plt.figure(figsize=(30,15))
	ax = fig.add_subplot(111)
	ax.set_title("SPEC 2017 Time Stats 500s - Scenario " + test[-1:] + " (input " + input_set + ')', fontsize=35)
	plt.xlabel("Benchmarks", fontsize=25)
	plt.ylabel("Performance slowdown", fontsize=25)
	# plt.xlim(0.0, 29)
	rects1 = ax.bar(ind, p1_loc, width, color='r')
	rects2 = ax.bar(ind+width, p1_rem, width, color='g')
	rects3 = ax.bar(ind+width*2, p1_inter, width, color='b')

	ax.set_xticks(ind+width)
	ax.set_xticklabels(p1_x_axis)
	ax.legend((rects1[0], rects2[0], rects3[0]), ('Local', 'Remote', 'Interleave'))

	if (absolute):
		plot_path = results_path + "/plots/500s_" + input_set + "_abs.png"
	else:
		plot_path = results_path + "/plots/500s_" + input_set + "_rel.png"

	plt.savefig(plot_path)

	# Plot for 600 series	
	ind = np.arange(len(p2_x_axis))
	width = 0.27
	fig = plt.figure(figsize=(30,15))
	ax = fig.add_subplot(111)
	ax.set_title("SPEC 2017 Time Stats 600s - Scenario " + test[-1:] + " (input " + input_set + ')', fontsize=35)
	plt.xlabel("Benchmarks", fontsize=25)
	plt.ylabel("Performance slowdown", fontsize=25)
	plt.xlim(0.0, 26.8)
	rects1 = ax.bar(ind, p2_loc, width, color='r')
	rects2 = ax.bar(ind+width, p2_rem, width, color='g')
	rects3 = ax.bar(ind+width*2, p2_inter, width, color='b')

	ax.set_xticks(ind+width)
	ax.set_xticklabels(p2_x_axis)
	ax.legend((rects1[0], rects2[0], rects3[0]), ('Local', 'Remote', 'Interleave'))

	if (absolute):
		plot_path = results_path + "/plots/600s_" + input_set + "_abs.png"
	else:
		plot_path = results_path + "/plots/600s_" + input_set + "_rel.png"

	plt.savefig(plot_path)
	# def autolabel(rects):
	# 	for rect in rects:
	# 		h = rect.get_height()
	# 		ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h), ha='center', va='bottom')

	# autolabel(rects1)
	# autolabel(rects2)
	# autolabel(rects3)




