import os
import csv

path = "/home/theovakalopoulos/Desktop/Diplomatiki/"
results_path = path + "results/test1/"
benchmarks = os.listdir(results_path)
names = []
for bench in sorted(benchmarks):

	if (not(bench.startswith('5') or bench.startswith('6'))):
		continue
	if (bench == "511" or bench == "627"):
		continue
	
	bench_dir = results_path + '/' + bench
	# List all output files inside benchmark's directory 
	files = os.listdir(bench_dir)
	for f in sorted(files):
		fp = open(bench_dir + '/' + f)
		lines = fp.readlines()

		for line in lines:
			tokens = line.split()
			if tokens:
				names.append(tokens[11])
				break
		break

output_file = path + "/scripts/bench_names.txt"
with open(output_file, mode='w') as f:
	for bench in names:
		f.write("%s\n" % bench)