from __future__ import division
import os
import threading
import sys
import subprocess
from cmd import Cmd
import time
import stat
import string
import csv
import random

flag = True
PIDs = {}
# threads_stop = {}
# open_files = {}
change_pages = {"flag": False, "num": 0, "src": -1, "dst": -1, "pick": ""}
log_file_path = os.getcwd() + "/perf_files/error.out"
log_file = None
chng_priority = {}
perf_interval = 5000 # in ms
# Dictionary with running processes perf counters
# "pid": {
# 	"CPI": value
# 	"BW": value
#	"mem_pages": array
#	"CPU_affinity": value
# }
process_info = {}

# Define number of nodes of the system
num_of_nodes = 4

# Define Distance Matrix
distances = [[10, 21, 21, 30], [21, 10, 30, 21], [21, 30, 10, 21], [30, 21, 21, 10]]


class CLIPrompt(Cmd):
	prompt = "->"
	intro = "\n\t****************   NUMA Resource Manager   ****************\n\nType ? to list commands\n"

	def do_migrate(self, inp):
		global change_pages
		
		inp = inp.split(" ")
		src = int(inp[0])
		dst = int(inp[1])
		num = int(inp[2])

		if (change_pages["flag"]):
			print("\nCan not malloc pages. Another memory process is still running.")
		elif ( src < 0 or src > 3 or dst < 0 or dst > 3):
			print("\nWrong source or destination node.")
		else:
			change_pages["flag"] = False
			change_pages["num"] = num
			change_pages["src"] = src
			change_pages["dst"] = dst
			print("Migrate " + inp[0] + " pages from node " + inp[1] + " to node " + inp[2])

	def do_free(self, inp):
		global change_pages

		if (change_pages["flag"]):
			print("\nCan not malloc pages. Another memory process is still running.")
		else:
			change_pages["flag"] = True
			change_pages["num"] = int(inp)
			change_pages["type"] = "free"
			print("Free " + inp + " pages from node 0")


	def do_increase(self, inp):
		global PIDs
		global chng_priority

		if (int(inp) in PIDs.keys()):
			print("Increase priority of PID " + inp + " to high")
			chng_priority[int(inp)]="high"
		else:
			print("Invalid PID")

	def do_decrease(self, inp):
		global PIDs
		global chng_priority

		if (int(inp) in PIDs.keys()):
			print("Decrease priority of PID " + inp + " to low")
			chng_priority[int(inp)]="low"
		else:
			print("Invalid PID")

	def do_exit(self, inp):
		print("Terminating resource manager...")
		return True

	def default(self, inp):
		if (inp=='q' or inp=='Q'):
			return self.do_exit(inp)

# Thread function for reading user input
def read(lock):
	CLIPrompt().cmdloop()
	lock.acquire()
	global flag
	flag = False
	lock.release()

# Thread function for running perf for every process
# def run_perf(cmd, pid):
# 	global threads_stop
# 	# print("Inside thread with cmd: " + cmd)
# 	while (True):	
# 		if (threads_stop[pid] == False):
# 			try:
# 				# os.system(cmd)
# 				f = open("/various/diplom/thvak/spec-2017/perf_files/error.log", "w")
# 				subprocess.check_output(cmd, stdout=f)
# 				print("Successful run completed")
# 			except subprocess.CalledProcessError:
# 				print("Error")
# 				return
# 		else:
# 			print("Stopping thread")
# 			return

def apply_model(params):

	open_files = params["open_files"]
	BW_file = params["BW_file"]
	bench_log_file = params["bench_log_file"]

	print("Ready to appply model...")
	bench_log_file.write("\nReady to appply model...")

	global PIDs
	global process_info, log_file, change_pages
	overall_mem_pages = [0] * 4

	lines = BW_file.readlines()

	if lines:
		last_iteration = lines[-1:][0]
		# print(last_iteration)
		if not last_iteration.startswith(';'):
			tokens = last_iteration.split(';')
			new_tokens = []
			for token in tokens:
				new_tokens.append(token.strip())

			try:
				BW_node_0 = float(new_tokens[9])
				BW_node_1 = float(new_tokens[17])
				BW_node_2 = float(new_tokens[25])
				BW_node_3 = float(new_tokens[33])
				Total_BW = float(new_tokens[36])
				print("BW Stats: node 0: " + str(BW_node_0) + "  node 1: " + str(BW_node_1) + "  node 2: " + str(BW_node_2) + "  node 3: " + str(BW_node_3) + "  Total: " + str(Total_BW))
				bench_log_file.write("\nBW Stats: node 0: " + str(BW_node_0) + "  node 1: " + str(BW_node_1) + "  node 2: " + str(BW_node_2) + "  node 3: " + str(BW_node_3) + "  Total: " + str(Total_BW))
			except IndexError:
				print("BW Stats index error")
				bench_log_file.write("\nBW Stats index error")

	# Loop over running PIDs to collect updated perf counters
	for pid in PIDs.keys():
		# print('Inside loop Open file: ' + str(open_files[pid]))
		lines = open_files[pid].readlines()

		# If perf output file is empty
		if not lines:
			continue

		# Fetch last update to perf output file
		last_iteration = lines[-4:]
		# print(last_iteration)
		try:
			perf_counters = []
			for line in last_iteration:
				tokens = line.split()
				perf_counters.append(int(tokens[1]))

			cycles = perf_counters[0]
			instructions = perf_counters[1]

			if (cycles != 0 and instructions != 0):
				process_info[pid]["CPI"] = float(cycles / instructions)

			if perf_interval:	
				process_info[pid]["BW"] = (perf_counters[2] + perf_counters[3]) / perf_interval

		except ValueError:
			log_file.write("\nError in fetching performance counters of process with pid " + str(pid))
		
		print("\tPID: " + str(pid) + '\t' + PIDs[pid]["name"] + "\tCPI: " + str(process_info[pid]["CPI"]) + "\tBW: " + str(process_info[pid]["BW"]))
		bench_log_file.write("\n\tPID: " + str(pid) + '\t' + PIDs[pid]["name"] + "\tCPI: " + str(process_info[pid]["CPI"]) + "\tBW: " + str(process_info[pid]["BW"]))
		# Fetch memory allocation of process in numa system
		numa_file_path = "/proc/" + str(pid) + "/numa_maps"
		try:
			numa_file = open(numa_file_path, "r")
			lines = numa_file.readlines()
			numa_file.close()
		except (OSError,IOError):
			log_file.write("\nCould not open file " + numa_file_path)

		node = [0] * 4
		for line in lines:
			tokens = line.split()
			for token in tokens:
				if token.startswith("N0"):
					node[0] = node[0] + int(token[3:])
					overall_mem_pages[0] = overall_mem_pages[0] + int(token[3:])
				elif token.startswith("N1"):
					node[1] = node[1] + int(token[3:])
					overall_mem_pages[1] = overall_mem_pages[1] + int(token[3:])
				elif token.startswith("N2"):
					node[2] = node[2] + int(token[3:])
					overall_mem_pages[2] = overall_mem_pages[2] + int(token[3:])
				elif token.startswith("N3"):
					node[3] = node[3] + int(token[3:])
					overall_mem_pages[3] = overall_mem_pages[3] + int(token[3:])

		process_info[pid]["mem_pages"] = node
		node_sum = node[0] + node[1] + node[2] + node[3]
		print("\tMemory allocation: node 0: " + str(node[0]) + "  node 1: " + str(node[1]) + "  node 2: " + str(node[2]) + "  node 3: " + str(node[3]) + "  Total: " + str(node_sum))
		bench_log_file.write("\n\tMemory allocation: node 0: " + str(node[0]) + "  node 1: " + str(node[1]) + "  node 2: " + str(node[2]) + "  node 3: " + str(node[3]) + "  Total: " + str(node_sum))
		# Fetch CPU affinity
		try:
			res = subprocess.check_output(['taskset', '-p', str(pid)])
			res = res.decode('ASCII')
			tokens = res.split()
			cpu_affinity = tokens[5]
			process_info[pid]["cpu_affinity"] = cpu_affinity
			print("\tCurrent CPU affinity: " + cpu_affinity)
			bench_log_file.write("\n\tCurrent CPU affinity: " + cpu_affinity)
		except subprocess.CalledProcessError:
			log_file.write("\nCould not fetch CPU affinity for process with pid " + str(pid))

		max_memory_node = node.index(max(node))
		# print("Max memory node: ", max_memory_node)
		
		# Default CPU affinity per node
		node_cpu = ["ff000000ff", "ff000000ff00", "ff000000ff0000", "ff000000ff000000"]

		if (PIDs[pid]["priority"] == "high"):
			# If process is of high priority gather all memory pages to one node and migrate CPU to
			# corresponding node in order to run locally
			# print("\tHigh priority")
			for i in range(0,3):
				if (i == max_memory_node):
					continue
				try:
					res = subprocess.check_output(['migratepages', str(pid), str(i), str(max_memory_node)])
					print("\tMigrated pages of process woth PID " + str(pid) + " from node " + str(i) + " to node " + str(max_memory_node))
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(pid))

			if (cpu_affinity != node_cpu[max_memory_node]):
				try:
					res = subprocess.check_output(['taskset', '-p', node_cpu[max_memory_node], str(pid)])
					print("\tChanged CPU affinity for process with PID " + str(pid) + " to " + node_cpu[max_memory_node])
				except subprocess.CalledProcessError:
					log_file.write("\nError in changing CPU affinity of process with pid " + str(pid))
		# else:
			# print("\tLow priority")

	print("System Overall Memory allocation: node 0: " + str(overall_mem_pages[0]) + "  node 1: " + str(overall_mem_pages[1]) + "  node 2: " + str(overall_mem_pages[2]) + "  node 3: " + str(overall_mem_pages[3]))
	bench_log_file.write("\nSystem Overall Memory allocation: node 0: " + str(overall_mem_pages[0]) + "  node 1: " + str(overall_mem_pages[1]) + "  node 2: " + str(overall_mem_pages[2]) + "  node 3: " + str(overall_mem_pages[3]))

	# If user wants page migration
	if (change_pages["flag"]):

		# If random policy enabled pick benchmarks randomly so as to migrate pages
		if (change_pages["pick"] == "random"):
			BWs_arr = []
			for pid in PIDs.keys():
				# High priority benchmarks are not affected by page migration
				if (PIDs[pid]["priority"] == "low"):
					BWs_arr.append((pid, process_info[pid]["BW"]))

			random.shuffle(BWs_arr)

			print("\nRandom BW array:")
			bench_log_file.write("\n\nRandom BW array")
			for item in BWs_arr:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			total_pages = 0
			for item in BWs_arr:
				try:
					pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
					total_pages = total_pages + pages
					# print("\nTotal pages: " + str(total_pages))
					pages_to_migrate = pages
					
					if (total_pages > change_pages["num"]):
						pages_to_migrate = change_pages["num"] - total_pages + pages
					
					res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
					
					print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
					bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

					if (total_pages > change_pages["num"]):
						change_pages["flag"] = False
						break
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			if (total_pages < change_pages["num"]):
				print("Can not migrate any more pages!")
				bench_log_file.write("\n\tCan not migrate any more pages")
				change_pages["flag"] = False

		# If best policy enabled apply below logic	
		elif (change_pages["pick"] == "best"):
			BWs_loc = []
			BWs_rem = []
			for pid in PIDs.keys():
				# High priority benchmarks are not affected by page migration
				if (PIDs[pid]["priority"] == "low"):
					if (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["dst"]]):
						BWs_loc.append((pid, process_info[pid]["BW"]))
					else:
						BWs_rem.append((pid, process_info[pid]["BW"]))

			# Sort local (to dst node) benchmarks in descending BW order
			BWs_loc.sort(key=lambda tuple: tuple[1], reverse=True)
			print("\n\tLocal BW array:")
			bench_log_file.write("\n\n\tLocal BW array")
			for item in BWs_loc:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort remote (to dst node) benchmarks in ascending BW order
			BWs_rem.sort(key=lambda tuple: tuple[1])
			print("\n\tRemote BW array:")
			bench_log_file.write("\n\n\tRemote BW array")
			for item in BWs_rem:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			total_pages = 0

			# Start migrating pages of benchmarks running on dst node cpu
			# in order to increase the proportion of their local memory
			for item in BWs_loc:
				try:
					pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
					total_pages = total_pages + pages
					# print("\nTotal pages: " + str(total_pages))
					pages_to_migrate = pages
					
					if (total_pages > change_pages["num"]):
						pages_to_migrate = change_pages["num"] - total_pages + pages
					
					res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
					
					print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
					bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

					if (total_pages >= change_pages["num"]):
						change_pages["flag"] = False
						break
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on remote nodes (to dst node)
			if change_pages["flag"]:

				for item in BWs_rem:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			if (total_pages < change_pages["num"]):
				print("Can not migrate any more pages!")
				bench_log_file.write("\n\tCan not migrate any more pages")
				change_pages["flag"] = False

		# If best policy enabled apply below logic	
		elif (change_pages["pick"] == "best+"):
			BWs_loc = []
			BWs_rem = []
			BWs_other = []

			for pid in PIDs.keys():
				# High priority benchmarks are not affected by page migration
				if (PIDs[pid]["priority"] == "low"):
					if (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["dst"]]):
						BWs_loc.append((pid, process_info[pid]["BW"]))
					elif (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["src"]]):
						BWs_rem.append((pid, process_info[pid]["BW"]))
					else:
						BWs_other.append((pid, process_info[pid]["BW"]))

			# Sort local (to dst node) benchmarks in descending BW order
			BWs_loc.sort(key=lambda tuple: tuple[1], reverse=True)
			print("\n\tLocal BW array:")
			bench_log_file.write("\n\n\tLocal BW array")
			for item in BWs_loc:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort local (to src node) benchmarks in ascending BW order
			BWs_rem.sort(key=lambda tuple: tuple[1])
			print("\n\tRemote BW array:")
			bench_log_file.write("\n\n\tRemote BW array")
			for item in BWs_rem:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort remote (to src and dst node) benchmarks in ascending BW order
			BWs_other.sort(key=lambda tuple: tuple[1])
			print("\n\tOther BW array:")
			bench_log_file.write("\n\n\tOther BW array")
			for item in BWs_other:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			total_pages = 0

			# Start migrating pages of benchmarks running on dst node cpu
			# in order to increase the proportion of their local memory
			for item in BWs_loc:
				try:
					pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
					total_pages = total_pages + pages
					# print("\nTotal pages: " + str(total_pages))
					pages_to_migrate = pages
					
					if (total_pages > change_pages["num"]):
						pages_to_migrate = change_pages["num"] - total_pages + pages
					
					res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
					
					print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
					bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

					if (total_pages >= change_pages["num"]):
						change_pages["flag"] = False
						break
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on remote nodes (to src and dst node)
			if change_pages["flag"]:

				for item in BWs_other:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))	

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on src node
			if change_pages["flag"]:

				for item in BWs_rem:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			if (total_pages < change_pages["num"]):
				print("Can not migrate any more pages!")
				bench_log_file.write("\n\tCan not migrate any more pages")
				change_pages["flag"] = False

		elif (change_pages["pick"] == "worst"):
			BWs_loc = []
			BWs_rem = []
			for pid in PIDs.keys():
				# High priority benchmarks are not affected by page migration
				if (PIDs[pid]["priority"] == "low"):
					if (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["dst"]]):
						BWs_loc.append((pid, process_info[pid]["BW"]))
					else:
						BWs_rem.append((pid, process_info[pid]["BW"]))

			# Sort local (to dst node) benchmarks in ascending BW order
			BWs_loc.sort(key=lambda tuple: tuple[1])
			print("\n\tLocal BW array:")
			bench_log_file.write("\n\n\tLocal BW array")
			for item in BWs_loc:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort remote (to dst node) benchmarks in descending BW order
			BWs_rem.sort(key=lambda tuple: tuple[1], reverse=True)
			print("\n\tRemote BW array:")
			bench_log_file.write("\n\n\tRemote BW array")
			for item in BWs_rem:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			total_pages = 0

			# Start migrating pages of benchmarks running on dst node cpu
			# in order to increase the proportion of their local memory
			for item in BWs_rem:
				try:
					pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
					total_pages = total_pages + pages
					# print("\nTotal pages: " + str(total_pages))
					pages_to_migrate = pages
					
					if (total_pages > change_pages["num"]):
						pages_to_migrate = change_pages["num"] - total_pages + pages
					
					res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
					
					print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
					bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

					if (total_pages >= change_pages["num"]):
						change_pages["flag"] = False
						break
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on remote nodes (to dst node)
			if change_pages["flag"]:

				for item in BWs_loc:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			if (total_pages < change_pages["num"]):
				print("Can not migrate any more pages!")
				bench_log_file.write("\n\tCan not migrate any more pages")
				change_pages["flag"] = False

		elif (change_pages["pick"] == "worst+"):
			BWs_loc = []
			BWs_rem = []
			BWs_other = []
			for pid in PIDs.keys():
				# High priority benchmarks are not affected by page migration
				if (PIDs[pid]["priority"] == "low"):
					if (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["dst"]]):
						BWs_loc.append((pid, process_info[pid]["BW"]))
					elif (process_info[pid]["cpu_affinity"] == node_cpu[change_pages["src"]]):
						BWs_rem.append((pid, process_info[pid]["BW"]))
					else:
						BWs_other.append((pid, process_info[pid]["BW"]))

			# Sort local (to dst node) benchmarks in ascending BW order
			BWs_loc.sort(key=lambda tuple: tuple[1])
			print("\n\tLocal BW array:")
			bench_log_file.write("\n\n\tLocal BW array")
			for item in BWs_loc:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort remote (to src and dst node) benchmarks in descending BW order
			BWs_other.sort(key=lambda tuple: tuple[1], reverse=True)
			print("\n\tOther BW array:")
			bench_log_file.write("\n\n\tOther BW array")
			for item in BWs_other:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			# Sort local (to src node) benchmarks in descending BW order
			BWs_rem.sort(key=lambda tuple: tuple[1], reverse=True)
			print("\n\tRemote BW array:")
			bench_log_file.write("\n\n\tRemote BW array")
			for item in BWs_rem:
				print("\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))
				bench_log_file.write("\n\tPid: " + str(item[0]) + "\tBW: " + str(item[1]))

			total_pages = 0

			# Start migrating pages of benchmarks running on src node cpu
			# in order to increase the proportion of their local memory
			for item in BWs_rem:
				try:
					pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
					total_pages = total_pages + pages
					# print("\nTotal pages: " + str(total_pages))
					pages_to_migrate = pages
					
					if (total_pages > change_pages["num"]):
						pages_to_migrate = change_pages["num"] - total_pages + pages
					
					res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
					
					print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
					bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

					if (total_pages >= change_pages["num"]):
						change_pages["flag"] = False
						break
				except subprocess.CalledProcessError:
					log_file.write("\nError in migrating pages of process with pid " + str(item[0]))	

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on remote nodes (to src and dst node)
			if change_pages["flag"]:

				for item in BWs_other:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			# continue with benchmarks running on remote nodes (to dst node)
			if change_pages["flag"]:

				for item in BWs_loc:
					try:
						pages = process_info[item[0]]["mem_pages"][change_pages["src"]]
						total_pages = total_pages + pages
						# print("\nTotal pages: " + str(total_pages))
						pages_to_migrate = pages
						
						if (total_pages > change_pages["num"]):
							pages_to_migrate = change_pages["num"] - total_pages + pages
						
						res = subprocess.check_output(['migratepages', str(item[0]), str(change_pages["src"]), str(change_pages["dst"])])
						
						print("\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
						bench_log_file.write("\n\tMigrated " + str(pages) + " pages of process with PID " + str(item[0]) + " from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))

						if (total_pages >= change_pages["num"]):
							change_pages["flag"] = False
							break
					except subprocess.CalledProcessError:
						log_file.write("\nError in migrating pages of process with pid " + str(item[0]))		

			# If total_pages migrated are less than those specified in the input command
			if (total_pages < change_pages["num"]):
				print("Can not migrate any more pages!")
				bench_log_file.write("\n\tCan not migrate any more pages")
				change_pages["flag"] = False


def get_benchmarks():
	path = "/various/diplom/thvak/spec-2017/"
	benchmarks = os.listdir(path)
	param_names = []
	exe_names = []
	for bench in sorted(benchmarks):
		if (not(bench.startswith('5') or bench.startswith('6'))):
			continue
		if (bench.startswith("511") or bench.startswith("627")):
			continue

		exe_names.append(bench[4:] + "_base.dunnington-x86-m64")
		param_names.append(bench)

	# Modifications
	exe_names[1] = "cpu" + exe_names[1]
	exe_names[exe_names.index("cactuBSSN_r_base.dunnington-x86-m64")] = "cactusBSSN_r_base.dunnington-x86-m64"
	exe_names[exe_names.index("bwaves_s_base.dunnington-x86-m64")] = "speed_bwaves_base.dunnington-x86-m64"
	exe_names[exe_names.index("roms_s_base.dunnington-x86-m64")] = "sroms_base.dunnington-x86-m64"
	exe_names[exe_names.index("pop2_s_base.dunnington-x86-m64")] = "speed_pop2_base.dunnington-x86-m64"
	exe_names[exe_names.index("gcc_s_base.dunnington-x86-m64")] = "sgcc_base.dunnington-x86-m64"
	exe_names[exe_names.index("xalancbmk_r_base.dunnington-x86-m64")] = "cpuxalan_r_base.dunnington-x86-m64"

	return {"param_names": param_names, "exe_names": exe_names}

def stress_system(benchmarks, input_type):
	# path = "/various/diplom/thvak/spec-2017/"
	# files = os.listdir(path)
	# cwd = os.getcwd()

	# for bench in benchmarks:
	# 	print(bench)
	# 	tokens = bench.split()
	# 	for file in files:
	# 		if file.startswith(tokens[0]):
	# 			path_to_bench = path + file + '/' + tokens[1] + '/'
	# 			items = os.listdir(path_to_bench)
	# 			for item in items:
	# 				if (tokens[1] + '-' + tokens[2]) in item:
	# 					file_path = path_to_bench + item
	# 					command_file = open(file_path, 'r')
	# 					cmd = command_file.readline()
	# 					parts = cmd.split()
	# 					cmd = string.replace(cmd, parts[0], parts[0] + ".dunnington-x86-m64")
	# 					print(cmd)
	# 					parts = cmd.split()
	# 					run_cmd = ["numactl", "-m", '0', "-N", '0', '--']
	# 					for part in parts:
	# 						run_cmd.append(part)
	# 					os.chdir(path_to_bench)
	# 					print("Current dir: " + os.getcwd())
	# 					# app = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# 					p = os.system("numactl -m 0 -N 0 -- ./perlbench_r_base.dunnington-x86-m64 -I./lib diffmail.pl 2 550 15 24 23 100 > diffmail.2.550.15.24.23.100.out 2>> diffmail.2.550.15.24.23.100.err 1> diffmail.2.550.15.24.23.100.out 2> diffmail.2.550.15.24.23.100.err &")
	# 					print(p)
	# 					break
	# 			break
	# os.chdir(cwd)

	# cmd = ["/home/users/vkarakos/tools/IntelPerformanceCounterMonitor-V2.11/pcm-memory.x", str(perf_interval/1000), "-csv="+BW_file_path]
	# BW_job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	benchmarks_str = ''
	cmd_files = ''
	configurations = ''
	for bench in benchmarks.keys():
		benchmarks_str = benchmarks_str + bench + ' '
		cmd_files += ("\"/various/diplom/thvak/spec-2017/" + bench + '/' + input_type + '/' + bench + "-cmd-" + input_type + '-' + str(benchmarks[bench][0]) + "\" ")
		configurations += "\"" + benchmarks[bench][1] + "\" "
	benchmarks_str = '\"' + benchmarks_str + '\"'

	shell_script_template_path = "/various/diplom/thvak/spec-2017/stress_system_template.sh"
	shell_script_template_file = open(shell_script_template_path, "r")
	lines = shell_script_template_file.readlines()

	for line in lines:
		if line.startswith("bench_list="):
			ind = lines.index(line)
			value = "bench_list=(" + benchmarks_str + ")\n"
			# print("Bench list: " + value)
			lines[ind] = value
		if line.startswith("cmd_files_list="):
			ind = lines.index(line)
			value = "cmd_files_list=(" + cmd_files + ")\n"
			# print("cmd_files_list: " + value)
			lines[ind] = value
		if line.startswith("input="):
			ind = lines.index(line)
			value = "input=\"" + input_type + "\"\n"
			lines[ind] = value
		if line.startswith("conf_arr="):
			ind = lines.index(line)
			value = "conf_arr=(" + configurations + ")\n"
			lines[ind] = value

	shell_script_template_file.close()

	shell_script_path = "/various/diplom/thvak/spec-2017/stress_system.sh"
	shell_script_file = open(shell_script_path, 'w+')
	shell_script_file.writelines(lines)
	shell_script_file.close()

	stress_script = subprocess.Popen("./stress_system.sh", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return stress_script

def main_task():
	global flag
	global change_pages
	flag = True
	lock = threading.Lock()

	# Reading thread running in background to wait asynchronously for user commands
	reading_thread = threading.Thread(target=read, args=(lock,))
	reading_thread.start()

	# Fetch benchmarks which can run on the system
	bench_names_file = "/various/diplom/thvak/spec-2017/bench_names.txt"
	res = get_benchmarks()
	benchmarks = res["exe_names"]
	names = res["param_names"]

	# Stress system with running applications
	conf=["-m 0 -N 0", "-m 1 -N 1", "-m 2 -N 2", "-m 3 -N 3"]
	input_type = "ref"
	extra_stressors = False

	# Start stressors
	if extra_stressors:
		os.system("numactl -m 0 -N 1 /home/users/vkarakos/tools/stress-ng/stress-ng --stream 8 &")
	
	# ____________Benchmarks to run_____________
	name = "conf3"
	series = "Test5"
	bench_log_file_path = "/various/diplom/thvak/results/resource_manager/" + series + '/' + name + "_log.txt"
	bench_log_file = open(bench_log_file_path, mode='w')
	# benchmarks_to_run = {"500.perlbench_r": [1,conf[0]], "508.namd_r": [1,conf[0]], "541.leela_r": [1,conf[0]], "544.nab_r": [1,conf[0]],"520.omnetpp_r": [1,conf[0]], "505.mcf_r": [1,conf[0]], "519.lbm_r": [1,conf[0]], "549.fotonik3d_r": [1,conf[0]]}
	# benchmarks_to_run = {"600.perlbench_s": [1,conf[0]], "641.leela_s": [1,conf[0]], "644.nab_s": [1,conf[0]], "648.exchange2_s": [1,conf[0]],"619.lbm_s": [1,conf[0]], "649.fotonik3d_s": [1,conf[0]], "654.roms_s": [1,conf[0]], "603.bwaves_s": [1,conf[0]]}
	
	# Testing senarios #
	benchmarks_to_run = []
	# Test 1
	# benchmarks_to_run = {"500.perlbench_r": [1,conf[0]], "508.namd_r": [1,conf[0]], "541.leela_r": [1,conf[0]], "544.nab_r": [1,conf[0]],"520.omnetpp_r": [1,conf[0]], "505.mcf_r": [1,conf[0]], "519.lbm_r": [1,conf[0]], "549.fotonik3d_r": [1,conf[0]], "600.perlbench_s": [1,conf[1]], "641.leela_s": [1,conf[1]], "644.nab_s": [1,conf[1]], "648.exchange2_s": [1,conf[1]],"619.lbm_s": [1,conf[1]], "649.fotonik3d_s": [1,conf[1]], "654.roms_s": [1,conf[1]], "603.bwaves_s": [1,conf[1]]}
	# stress_script = stress_system(benchmarks_to_run, input_type)
	# stress_script.wait()

	# Tests 2, 3, 4
	# benchmarks_to_run.append({"600.perlbench_s": [1,conf[0]], "641.leela_s": [1,conf[0]], "644.nab_s": [1,conf[0]], "648.exchange2_s": [1,conf[0]],"619.lbm_s": [1,conf[0]], "649.fotonik3d_s": [1,conf[0]], "654.roms_s": [1,conf[0]], "603.bwaves_s": [1,conf[0]]})
	# stress_script = stress_system(benchmarks_to_run[0], input_type)
	# stress_script.wait()
	# benchmarks_to_run.append({"600.perlbench_s": [1,conf[1]], "641.leela_s": [1,conf[1]], "644.nab_s": [1,conf[1]], "648.exchange2_s": [1,conf[1]],"619.lbm_s": [1,conf[1]], "649.fotonik3d_s": [1,conf[1]], "654.roms_s": [1,conf[1]], "603.bwaves_s": [1,conf[1]]})
	# stress_script = stress_system(benchmarks_to_run[1], input_type)
	# stress_script.wait()
	# benchmarks_to_run.append({"600.perlbench_s": [1,conf[2]], "641.leela_s": [1,conf[2]], "644.nab_s": [1,conf[2]], "648.exchange2_s": [1,conf[2]],"619.lbm_s": [1,conf[2]], "649.fotonik3d_s": [1,conf[2]], "654.roms_s": [1,conf[2]], "603.bwaves_s": [1,conf[2]]})
	# stress_script = stress_system(benchmarks_to_run[2], input_type)
	# stress_script.wait()
	# benchmarks_to_run.append({"600.perlbench_s": [1,conf[3]], "641.leela_s": [1,conf[3]], "644.nab_s": [1,conf[3]], "648.exchange2_s": [1,conf[3]],"619.lbm_s": [1,conf[3]], "649.fotonik3d_s": [1,conf[3]], "654.roms_s": [1,conf[3]], "603.bwaves_s": [1,conf[3]]})
	# stress_script = stress_system(benchmarks_to_run[3], input_type)
	# stress_script.wait()

	# Test 5
	benchmarks_to_run.append({"520.omnetpp_r": [1,conf[0]], "505.mcf_r": [1,conf[0]], "519.lbm_r": [1,conf[0]], "549.fotonik3d_r": [1,conf[0]],"619.lbm_s": [1,conf[0]], "649.fotonik3d_s": [1,conf[0]], "654.roms_s": [1,conf[0]], "603.bwaves_s": [1,conf[0]]})
	stress_script = stress_system(benchmarks_to_run[0], input_type)
	stress_script.wait()
	benchmarks_to_run.append({"520.omnetpp_r": [1,conf[1]], "505.mcf_r": [1,conf[1]], "519.lbm_r": [1,conf[1]], "549.fotonik3d_r": [1,conf[1]],"619.lbm_s": [1,conf[1]], "649.fotonik3d_s": [1,conf[1]], "654.roms_s": [1,conf[1]], "603.bwaves_s": [1,conf[1]]})
	stress_script = stress_system(benchmarks_to_run[1], input_type)
	stress_script.wait()
	benchmarks_to_run.append({"520.omnetpp_r": [1,conf[2]], "505.mcf_r": [1,conf[2]], "519.lbm_r": [1,conf[2]], "549.fotonik3d_r": [1,conf[2]],"619.lbm_s": [1,conf[2]], "649.fotonik3d_s": [1,conf[2]], "654.roms_s": [1,conf[2]], "603.bwaves_s": [1,conf[2]]})
	stress_script = stress_system(benchmarks_to_run[2], input_type)
	stress_script.wait()
	benchmarks_to_run.append({"520.omnetpp_r": [1,conf[3]], "505.mcf_r": [1,conf[3]], "519.lbm_r": [1,conf[3]], "549.fotonik3d_r": [1,conf[3]],"619.lbm_s": [1,conf[3]], "649.fotonik3d_s": [1,conf[3]], "654.roms_s": [1,conf[3]], "603.bwaves_s": [1,conf[3]]})
	stress_script = stress_system(benchmarks_to_run[3], input_type)
	stress_script.wait()

	bench_times = {}
	start_time = time.time()

	# Memory migration config
	automatic_page_migration = True
	migration_file_path = "/various/diplom/thvak/results/resource_manager/" + series + "/automatic_migration.txt"
	migration_file = open(migration_file_path, mode='r')
	commands = migration_file.readlines()
	number_of_migrations = len(commands)
	interval_between_migrations = 30
	change_pages["pick"] = "worst"
	previous_time = time.time()
	cmd_counter = 0

	# benchmarks_to_run = {}
	# for bench in names:
	# 	benchmarks_to_run[bench] = 1

	open_files = {}
	perf_jobs = {}
	previous_PIDs = {}

	# Initialise log file
	global log_file, log_file_path
	log_file = open(log_file_path, "w+")

	# Initialise BW reporting
	BW_file_path = os.getcwd() + "/perf_files/BW.csv"
	BW_file = open(BW_file_path, "w+")

	cmd = ["/home/users/vkarakos/tools/IntelPerformanceCounterMonitor-V2.11/pcm-memory.x", str(perf_interval/1000), "-csv="+BW_file_path]
	BW_job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Main Loop until resuorce manager is terminated by user
	while flag:
		print('\n')

		current_PIDs = {}

		# Automatic page migrations
		if ( automatic_page_migration and (time.time()-previous_time > interval_between_migrations) and (cmd_counter < number_of_migrations)):
			previous_time = time.time()
			cmd = commands[cmd_counter]
			args = cmd.split(" ")
			change_pages["flag"] = True
			change_pages["src"] = int(args[0])
			change_pages["dst"] = int(args[1])
			change_pages["num"] = int(args[2])
			print("Migrate " + str(change_pages["num"]) + " pages from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
			bench_log_file.write("\nMigrate " + str(change_pages["num"]) + " pages from node " + str(change_pages["src"]) + " to node " + str(change_pages["dst"]))
			cmd_counter = cmd_counter + 1

		# Get all PIDs of applications running on the system
		for bench in benchmarks:
			try:
				pid = subprocess.check_output(['pidof', bench])
				pid = pid.decode('ASCII')
				# Get all running instances for benchmark
				pids_arr = pid.split(" ")
				for pid in pids_arr:
					# print("PID: " + pid)
					ind = benchmarks.index(bench)
					try:
						input_num = str(benchmarks_to_run[0][names[ind]][0])
					except KeyError:
						input_num = "0"
					current_PIDs[int(pid)] = {"name": names[ind] + "-" + input_type + "-" + input_num + "-instance_" + str(pids_arr.index(pid)), "priority": "low", "simple_name": names[ind]}

			except subprocess.CalledProcessError:
				continue

		# Initialise perf output file for every new process running in the system
		for pid in list(current_PIDs):
			if pid in previous_PIDs.keys():
				continue
			try:
				print("\nProcess with PID " + str(pid) + " started running")
				bench_log_file.write("\n\nProcess with PID " + str(pid) + " started running")
				# File for perf output
				file_path = os.getcwd() + "/perf_files/" + str(pid) + ".out"
				f = open(file_path, "w+")

				# Create new entry in open files dictionary
				open_files[pid] = f

				# Initialise dictionary for current pid inside process_info dictionary
				process_info[pid] = {}
				process_info[pid]["CPI"] = -1
				process_info[pid]["BW"] = -1

				# Start a new thread to run perf for current pid
				cmd = ["perf_3.16", "stat", "-o", file_path, "-e", "cycles,instructions,LLC-load-misses,LLC-store-misses", "-p", str(pid), "-I", "5000"]
				# perf_thread = threading.Thread(target=run_perf, args=(cmd,pid,))

				# Create new entry in running threads dictionary
				# perf_threads[pid] = perf_thread
				# Create new entry in threads_stop dictionary
				# threads_stop[pid] = False
				# perf_thread.start()
				perf_job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# Create new entry in running perf processes dictionary
				perf_jobs[pid] = perf_job

			except subprocess.CalledProcessError:
				log_file.write("\nError in initialising perf reporting for PID: " + str(pid))

		# Stop perf for every process which stopped running since last iteration
		for pid in list(previous_PIDs):
			if pid in current_PIDs.keys():
				continue
			try:
				# Fetch running time for terminated bench
				time_file_path = "/various/diplom/thvak/spec-2017/perf_files/time_" + previous_PIDs[pid]["simple_name"] + ".out"
				time_file = open(time_file_path, 'r')
				lines = time_file.readlines()
				run_time = time.time() - start_time
				try:
					bench_time = lines[1].split()[1]
				except IndexError:
					bench_time = str(run_time)
				# bench_times[previous_PIDs[pid]["simple_name"]] = bench_time
				bench_times[previous_PIDs[pid]["name"]] = {"time": bench_time, "simple_name": previous_PIDs[pid]["simple_name"]}
				print("\nProcess with PID " + str(pid) + " terminated.\tTime: " + bench_time)
				bench_log_file.write("\n\nProcess " + previous_PIDs[pid]["name"] + " with PID " + str(pid) + " terminated.\tTime: " + bench_time)
				print("Run time: " + str(run_time))
				bench_log_file.write("\nRun time: " + str(run_time))


				del previous_PIDs[pid]
				del process_info[pid]
				# If process not running terminate perf_thread
				# threads_stop[pid] = True
				perf_jobs[pid].terminate()

				file_path = os.getcwd() + "/perf_files/" + str(pid) + ".out"
				if os.path.exists(file_path):
					os.remove(file_path)
					log_file.write("\nPerf file removed")
			except subprocess.CalledProcessError:
				log_file.write("\nError in terminating perf process for PID: " + str(pid))

		# Restore priority of every process which continues running on the system
		current_PIDs.update(previous_PIDs)

		# Update priority of processes according to user commands
		global chng_priority

		for pid in list(chng_priority):
			if (pid in current_PIDs.keys()):
				current_PIDs[pid]["priority"] = chng_priority[pid]

		chng_priority = {}

		if current_PIDs:
			print("Running processes PIDs, priorities and names (" + str(len(current_PIDs.keys())) + ')')
			bench_log_file.write("\nRunning processes PIDs, priorities and names (" + str(len(current_PIDs.keys())) + ')')
			for pid in current_PIDs:
				print("\tPID: " + str(pid) + '\t' + current_PIDs[pid]["priority"] + '\t' + current_PIDs[pid]["name"])
				bench_log_file.write("\n\tPID: " + str(pid) + '\t' + current_PIDs[pid]["priority"] + '\t' + current_PIDs[pid]["name"])
		else:
			end_time = time.time()
			total_time = end_time - start_time
			print("Total Time: " + str(total_time))
			bench_log_file.write("\nTotal Time: " + str(total_time))
			print("No process is running on the system")

		previous_PIDs = current_PIDs

		# Update global dictionary
		global PIDs
		PIDs = current_PIDs

		# Apply predefined model for running processes
		params = {"open_files": open_files, "BW_file": BW_file, "bench_log_file": bench_log_file}
		if current_PIDs:
			apply_model(params)

		time.sleep(5)

	reading_thread.join()

	# Save benchmarks running times
	try:
		ordered_benchmarks = []
		with open("/various/diplom/thvak/results/resource_manager/" + series + "/baseline.txt", 'r') as f:
			lines = f.readlines()
			for line in lines:
				tokens = line.split('\t')
				ordered_benchmarks.append(tokens[0])

		ordered_bench_times = []
		for bench in ordered_benchmarks:
			for key in bench_times.keys():
				item = bench_times[key]

				if item["simple_name"] == bench:
					try:
						tokens = item["time"].split('m')
						minutes = float(tokens[0])
						seconds = float(tokens[1][:-1])
						bench_time = minutes * 60 + seconds
					except IndexError:
						bench_time = "Error"
					ordered_bench_times.append([key, bench_time])		

		bench_times_file_path = "/various/diplom/thvak/results/resource_manager/" + series + '/' + name + ".txt"
		bench_times_file = open(bench_times_file_path, mode='w')
		file_writer = csv.writer(bench_times_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		file_writer.writerows(ordered_bench_times)
		bench_times_file.close()
	except KeyError:
		log_file.write("Could not fetch bench times.")

	# Terminate BW process and delete output file
	BW_job.terminate()
	os.remove(BW_file_path)

	# Kill stressors
	if extra_stressors:
		os.system("killall stress-ng")

	if automatic_page_migration:
		migration_file.close()

	# Kill remaining perf processes
	try:
		pids = subprocess.check_output(['pidof', "perf_3.16"])
		pids_arr = pids.split()
		for pid in pids_arr:
			# print("kill perf_process: "+str(pid))
			subprocess.check_output(["kill", "-9", pid])
	except subprocess.CalledProcessError:
		log_file.write("\nError in terminating perf processes")

	# Kill remaining pcm-memory.x processes
	try:
		pids = subprocess.check_output(['pidof', "pcm-memory.x"])
		pids_arr = pids.split()
		for pid in pids_arr:
			# print("kill perf_process: "+str(pid))
			subprocess.check_output(["kill", "-9", pid])
	except subprocess.CalledProcessError:
		log_file.write("\nError in terminating pcm-memory.x processes")

	# Kill remaining running applications
	try:
		for pid in current_PIDs.keys():
			# print("kill benchmark: " + str(pid))
			subprocess.check_output(["kill", "-9", str(pid)])
	except subprocess.CalledProcessError:
		print("Error")
		log_file.write("\nError in terminating perf processes")

	log_file.close()
	bench_log_file.close()
	# Point where all terminated perf_threads join
	# for thread in perf_threads.values():
		# thread.join()

if __name__ == "__main__":
	main_task()