#!/usr/bin/env python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv
import math

# Directory name of the results to plot 
test = sys.argv[1]
detailed = True
if (len(sys.argv) > 2):
	if (sys.argv[2] == "False"):
		detailed = False

path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/resource_manager/"

results_path = path_to_results + test

# Initialisations for plots
x_axis = []
x_axis_rel = []
confs = []
benchmarks = ["600", "641", "644", "648", "619", "649", "654", "603", "Overall Slowdown"]


# List all benchmarks files inside the results directory
files = os.listdir(results_path)
other_files = 0
for file in sorted(files):
	if (file.startswith('info') or file.startswith('overview') or file.startswith('baseline') or file.startswith('automatic') or file.startswith('plot') or ("log" in file)):
		other_files = other_files + 1
		continue

	file_dir = results_path + '/' + file

	fp = open(file_dir)
	lines = fp.readlines()
	conf = []
	for line in lines:
		tokens = line.split('\t')
		conf.append(float(tokens[1]))

	if (not x_axis):
		for line in lines:
			tokens = line.split('\t')
			x_axis.append(tokens[0])
			x_axis_rel.append(tokens[0])
	
	confs.append(conf)


num_of_confs = len(files) - other_files
rel_confs = []
baseline_conf = confs[0]
for conf in confs:
	rel_conf = []
	if (confs.index(conf) == 0):
		for item in conf:
			rel_conf.append(1.0)
	else:
		for item in conf:
			index = conf.index(item)
			rel_conf.append(round(conf[index] / baseline_conf[index], 3))
	
	rel_confs.append(rel_conf)


slowdowns = []
# Calculate slowdown of every set of similar benchmarks as the mean of benchmarks slowdowns
for rel_conf in rel_confs:
	current = []
	cnt = 0
	total = 0
	for item in rel_conf:
		if (cnt != 0 and cnt % 4 == 0):
			current.append(round(total / 4, 3))
			total = 0

		total = total + item
		cnt = cnt + 1
	current.append(round(total / 4, 3))

	slowdowns.append(current)


# Overall Slowdown as the geometric mean of benchmarks slowdowns
if detailed:
	for rel_conf in rel_confs:
		slowdown = 1
		for item in rel_conf:
			slowdown = slowdown * item
		slowdown = slowdown ** (1/len(rel_conf))
		ind = rel_confs.index(rel_conf)
		rel_conf.append(round(slowdown, 3))
		rel_confs[ind] = rel_conf
	x_axis_rel.append("Overall Slowdown")
else:
	for rel_conf in slowdowns:
		slowdown = 1
		for item in rel_conf:
			slowdown = slowdown * item
		slowdown = slowdown ** (1/len(rel_conf))
		ind = slowdowns.index(rel_conf)
		rel_conf.append(round(slowdown, 3))
		slowdowns[ind] = rel_conf

	rel_confs = slowdowns
	x_axis_rel = benchmarks


###########################
#### Save to csv files ####
csv_file = results_path + "/overview.csv"

data = []
if (num_of_confs == 2):
	data.append(["Benchmark", "Conf1", "Conf2"])
elif (num_of_confs == 3):
	data.append(["Benchmark", "Conf1", "Conf2", "Conf3"])
elif (num_of_confs == 4):
	data.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4"])
elif (num_of_confs == 5):
	data.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5"])
elif (num_of_confs == 6):
	data.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5", "Conf6"])
elif (num_of_confs == 7):
	data.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5", "Conf6", "Conf7"])

for i in range (len(x_axis)):
	if num_of_confs == 2:
		data.append([x_axis[i], confs[0][i], confs[1][i]])
	elif num_of_confs == 3:
		data.append([x_axis[i], confs[0][i], confs[1][i], confs[2][i]])
	elif num_of_confs == 4:
		data.append([x_axis[i], confs[0][i], confs[1][i], confs[2][i], confs[3][i]])
	elif num_of_confs == 5:
		data.append([x_axis[i], confs[0][i], confs[1][i], confs[2][i], confs[3][i], confs[4][i]])
	elif num_of_confs == 6:
		data.append([x_axis[i], confs[0][i], confs[1][i], confs[2][i], confs[3][i], confs[4][i], confs[5][i]])
	elif num_of_confs == 7:
		data.append([x_axis[i], confs[0][i], confs[1][i], confs[2][i], confs[3][i], confs[4][i], confs[5][i], confs[6][i]])

data_rel = []
if (num_of_confs == 2):
	data_rel.append(["Benchmark", "Conf1", "Conf2"])
elif (num_of_confs == 3):
	data_rel.append(["Benchmark", "Conf1", "Conf2", "Conf3"])
elif (num_of_confs == 4):
	data_rel.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4"])
elif (num_of_confs == 5):
	data_rel.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5"])
elif (num_of_confs == 6):
	data_rel.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5", "Conf6"])
elif (num_of_confs == 7):
	data_rel.append(["Benchmark", "Conf1", "Conf2", "Conf3", "Conf4", "Conf5", "Conf6", "Conf7"])

for i in range (len(x_axis_rel)):
	if num_of_confs == 2:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i]])
	elif num_of_confs == 3:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i], rel_confs[2][i]])
	elif num_of_confs == 4:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i], rel_confs[2][i], rel_confs[3][i]])
	elif num_of_confs == 5:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i], rel_confs[2][i], rel_confs[3][i], rel_confs[4][i]])
	elif num_of_confs == 6:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i], rel_confs[2][i], rel_confs[3][i], rel_confs[4][i], rel_confs[5][i]])
	elif num_of_confs == 7:
		data_rel.append([x_axis_rel[i], rel_confs[0][i], rel_confs[1][i], rel_confs[2][i], rel_confs[3][i], rel_confs[4][i], rel_confs[5][i], rel_confs[6][i]])

with open(csv_file, mode='w') as fl:
	file_writer = csv.writer(fl, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	file_writer.writerows(data)
	file_writer.writerows(data_rel)
	fl.close()

##########################
###### Create plots ######

# Plot (absolute performance)
ind = np.arange(len(x_axis))
if (num_of_confs < 4):
	width = 0.22
elif (num_of_confs < 6):
	width = 0.195
else:
	width = 0.13
fig = plt.figure(figsize=(30,15))
ax = fig.add_subplot(111)
ax.set_title("Resource Manager Static Tests - " + test, fontsize=20)
plt.xlabel("Benchmarks", fontsize=20)
plt.ylabel("Execution Time (seconds)", fontsize=20)

rects1 = ax.bar(ind, confs[0], width, color='r')
rects2 = ax.bar(ind+width, confs[1], width, color='g')
if num_of_confs > 2:
	rects3 = ax.bar(ind+width*2, confs[2], width, color='b')
if num_of_confs > 3:
	rects4 = ax.bar(ind+width*3, confs[3], width, color='y')
if num_of_confs > 4:
	rects5 = ax.bar(ind+width*4, confs[4], width, color='k')
if num_of_confs > 5:
	rects6 = ax.bar(ind+width*5, confs[5], width, color='c')
if num_of_confs > 6:
	rects7 = ax.bar(ind+width*6, confs[6], width, color='m')

ax.set_xticks(ind+2*width)
ax.set_xticklabels(x_axis)
if num_of_confs == 2:
	ax.legend((rects1[0], rects2[0]), ('Conf1', 'Conf2'))
elif num_of_confs == 3:
	ax.legend((rects1[0], rects2[0], rects3[0]), ('Conf1', 'Conf2', 'Conf3'))
elif num_of_confs == 4:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('Conf1', 'Conf2', 'Conf3', 'Conf4'))
elif num_of_confs == 5:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('Best', 'Random', 'Random', 'Random', 'Worst'))
elif num_of_confs == 6:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0]), ('Conf1', 'Conf2', 'Conf3', 'Conf4', 'Conf5', 'Conf6'))
elif num_of_confs == 7:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0], rects7[0]), ('Conf0', 'Conf1', 'Conf2', 'Conf3', 'Conf4', 'Conf5', 'Conf6'))

plot_path = results_path + "/plot_abs.png"

plt.savefig(plot_path)

# Plot (relative performance)
ind = np.arange(len(x_axis_rel))
if (num_of_confs < 4):
	width = 0.21
elif (num_of_confs < 6):
	width = 0.18
else:
	width = 0.13
fig = plt.figure(figsize=(30,15))
ax = fig.add_subplot(111)
ax.set_title("Resource Manager Dynamic Tests - " + test, fontsize=20)
plt.xlabel("Benchmarks", fontsize=20)
plt.ylabel("Performance slowdown", fontsize=20)


rects1 = ax.bar(ind, rel_confs[0], width, color='r')
rects2 = ax.bar(ind+width, rel_confs[1], width, color='g')
if num_of_confs > 2:
	rects3 = ax.bar(ind+width*2, rel_confs[2], width, color='b')
if num_of_confs > 3:
	rects4 = ax.bar(ind+width*3, rel_confs[3], width, color='y')
if num_of_confs > 4:
	rects5 = ax.bar(ind+width*4, rel_confs[4], width, color='k')
if num_of_confs > 5:
	rects6 = ax.bar(ind+width*5, rel_confs[5], width, color='c')
if num_of_confs > 6:
	rects7 = ax.bar(ind+width*6, rel_confs[6], width, color='m')

ax.set_xticks(ind+3*width)
ax.set_xticklabels(x_axis_rel)
if num_of_confs == 2:
	ax.legend((rects1[0], rects2[0]), ('Conf1', 'Conf2'))
elif num_of_confs == 3:
	ax.legend((rects1[0], rects2[0], rects3[0]), ('Conf1', 'Conf2', 'Conf3'))
elif num_of_confs == 4:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('Best', 'Best+', 'Worst', 'Worst+'))
elif num_of_confs == 5:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('Best', 'Random', 'Random', 'Random', 'Worst'))
elif num_of_confs == 6:
	ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0]), ('Best', 'Random', 'Random', 'Random', 'Random', 'Worst'))
elif num_of_confs == 7:
		ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0], rects6[0], rects7[0]), ('Best', 'Random', 'Random', 'Random', 'Worst', 'Best+', 'Worst+'))

plot_path = results_path + "/plot_rel.png"

plt.savefig(plot_path)

def autolabel(rects):
	for rect in rects:
		h = rect.get_height()
		ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h), ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
if (num_of_confs == 3):
	autolabel(rects3)
if (num_of_confs == 4):
	autolabel(rects4)
if (num_of_confs == 5):
	autolabel(rects5)
if (num_of_confs == 6):
	autolabel(rects6)
if (num_of_confs == 7):
	autolabel(rects7)