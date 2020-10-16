#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv

effect_id = sys.argv[1]
results_path = "/home/theovakalopoulos/Desktop/Diplomatiki/results/stress_effect_" + effect_id + '/'
files = os.listdir(results_path)
loc_list = []
rem_list = []
inter_list = []

for file in sorted(files):
	if (".png" in file):
		continue
	fp = open(results_path + file)
	lines = fp.readlines()
	perf_counters = []

	for line in lines:
		tokens = line.split()
		if tokens:
			perf_counters.append(tokens[0])

	time = float(perf_counters[-1])
	if ("conf_0" in file):
		if ("stress_10" in file):
			loc_10 = time
		else:
			loc_list.append(time)
	elif ("conf_1" in file):
		if ("stress_10" in file):
			rem_10 = time
		else:
			rem_list.append(time)
	else:
		if ("stress_10" in file):
			inter_10 = time
		else:
			inter_list.append(time)

if (effect_id != "2_4"):
	loc_list.append(loc_10)

rem_list.append(rem_10)
inter_list.append(inter_10)

if (effect_id != "2_4"):
	base = loc_list[0]
else:
	base = rem_list[0]

if (effect_id != "2_4"):
	loc_list = [ e / base for e in loc_list]

rem_list = [ e / base for e in rem_list]
inter_list = [ e / base for e in inter_list]

x_axis = ['0', '1', '2', '4', '6', '8', '10']

ind = np.arange(len(x_axis))
width = 0.27
fig = plt.figure(figsize=(30,15))
ax = fig.add_subplot(111)
ax.set_title("Comparison for different number of stressors for 520")

if (effect_id != "2_4"):
	rects1 = ax.bar(ind, loc_list, width, color='r')
	rects2 = ax.bar(ind+width, rem_list, width, color='g')
	rects3 = ax.bar(ind+width*2, inter_list, width, color='b')
	ax.set_xticks(ind+1.4*width)
	ax.set_xticklabels(x_axis)
	ax.legend((rects1[0], rects2[0], rects3[0]), ('Local', 'Remote', 'Interleave'))
else:
	rects1 = ax.bar(ind, rem_list, width, color='g')
	rects2 = ax.bar(ind+width, inter_list, width, color='b')
	ax.set_xticks(ind+width)
	ax.set_xticklabels(x_axis)
	ax.legend((rects1[0], rects2[0]), ('Remote', 'Interleave'))

plot_path = results_path + "stress_comparison.png"
plt.savefig(plot_path)
