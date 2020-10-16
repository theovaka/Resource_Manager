#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import csv
import math
import itertools
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_absolute_error
from operator import itemgetter
from lmfit import Model

conf = []

def function_generator1():
	def make_function(x, n, op):
		def Re_num(s):
			ret = ''; j = 0; k = 1
			for i in s:
				if i == 'a':
					ret += i+str(j); j += 1
				elif i == 'x':
					ret += i; k += 1
				else:
					ret += i
			return ret+' + b'

		prod = []
		for i in x:
			prod.append(list(itertools.product([i], n)))
		if op == 2:
			prod[0] = list(itertools.product(prod[0], n))
		prod = list(itertools.product(*prod)); ret = []
		for i in prod:
			if op == 0:
				j = list(i[0])
				t1 = 'a*'+j[0]+'**('+j[1]+')'
				t2 = j[0]+'**('+j[1]+')'
				length = len(i)
			if op == 1:
				j = list(i[0])
				t1 = 'a*log('+j[0]+'+1)**('+j[1]+')'
				t2 = j[0]+'**('+j[1]+')'
				length = len(i)
			elif op == 2:
				j = list(i[0][0])+[i[0][1]]
				t1 = 'a*log('+j[0]+'+1)**('+j[1]+') + a*'
				t1 += j[0]+'**('+j[2]+')'
				t2 = j[0]+'**('+j[1]+')'
				length = len(i)+1
			t3 = []
			for j in i[1:]: t3.append(j[0]+'**('+j[1]+')')
			
			main = (' + a*'.join([t1]+t3))
			ret.append(Re_num(main))
			tt = [t2]+t3
			temp = []
			for j in range(2, len(tt)+1):
				for subset in itertools.combinations(tt, j):
					temp.append('a*('+(')*('.join(subset))+')')
			for j in range(1, len(temp)+1):
				for subset in itertools.combinations(temp, j):
					if length+len(subset) >= 8: continue
					a = Re_num(main+' + '+(' + '.join(subset)))
					if a != '': ret.append(a)
		return ret
		
	x = ['x1', 'x2', 'x3', 'x4']
	n = list(np.arange(-2, 2+0.1, 0.5)); n.remove(0)
	n = [str(i) for i in n]
	ret = []
	for i in range(1, len(x)+1):
		for subset in itertools.combinations(x, i):
			ret += make_function(list(subset), n, 0)
			for j in subset:
				t = list(subset); t.remove(j); t = [j]+t
				ret += make_function(t, n, 1)
				ret += make_function(t, n, 2)
			print(ret)
	print(ret)
	return ret

def convert_to_var(x, param):
	if (param == 'x1'):
		return x[:,0]
	elif (param == 'x2'):
		return x[:,1]
	elif (param == 'x3'):
		return x[:,2]
	else:
		return x[:,3]

def function_generator():
	# Main term
	exp = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]
	var = ['x1', 'x2', 'x3', 'x4']
	sel1 = [var, exp]
	list1 = list(itertools.product(*sel1))

	# Secondary terms
	exp = [-2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0]
	sel2 = [exp, exp, exp, exp]
	list2 = list(itertools.product(*sel2))

	# Correlation terms
	flag = [0, 1]
	sel3 = [flag, flag, flag, flag, flag, flag]
	list3 = list(itertools.product(*sel3))
	# list3 = list(dict.fromkeys(list3))

	sel4 = [list1, list2, list3]
	list4 = list(itertools.product(*sel4))
	return list4

def limit_func(conf):
	cond1 = conf[2][0] == 1 and (conf[1][0] == 0 or conf[1][1] == 0)
	cond2 = conf[2][1] == 1 and (conf[1][0] == 0 or conf[1][2] == 0)
	cond3 = conf[2][2] == 1 and (conf[1][0] == 0 or conf[1][3] == 0)
	cond4 = conf[2][3] == 1 and (conf[1][1] == 0 or conf[1][2] == 0)
	cond5 = conf[2][4] == 1 and (conf[1][1] == 0 or conf[1][3] == 0)
	cond6 = conf[2][5] == 1 and (conf[1][2] == 0 or conf[1][3] == 0)

	# cond7 = conf[0][0] == 'x1' and conf[0][1] != conf[1][0]
	# cond8 = conf[0][0] == 'x2' and conf[0][1] != conf[1][1]
	# cond9 = conf[0][0] == 'x3' and conf[0][1] != conf[1][2]
	# cond10 = conf[0][0] == 'x4' and conf[0][1] != conf[1][3]

	cnt = 0
	for i in range(0,3):
		if (conf[1][i] != 0):
			cnt += 1
	for i in range(0,5):
		if (conf[2][i] != 0):
			cnt += 1

	if (cond1 or cond2 or cond3 or cond4 or cond5 or cond6 or (cnt > 6)):	
		return True
	else:
		return False

def init_predictor(x, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, b0):
	x1 = x[:,0]
	x2 = x[:,1]
	x3 = x[:,2]
	x4 = x[:,3]

	x1_pw = np.power(x1, conf[1][0])
	x2_pw = np.power(x2, conf[1][1])
	x3_pw = np.power(x3, conf[1][2])
	x4_pw = np.power(x4, conf[1][3])

	# Main term
	temp = np.log10(convert_to_var(x, conf[0][0]) + 1)
	t1 = a0 * np.power(temp, conf[0][1])

	# Secondary terms
	t2 = a1 * x1_pw
	t3 = a2 * x2_pw
	t4 = a3 * x3_pw
	t5 = a4 * x4_pw

	# Correlation terms
	if (conf[0][0] == 'x1'):
		t6 = a5 * np.power(x1, conf[0][1]) * x2_pw
		t7 = a6 * np.power(x1, conf[0][1]) * x3_pw
		t8 = a7 * np.power(x1, conf[0][1]) * x4_pw
		t9 = a8 * x2_pw * x3_pw
		t10 = a9 * x2_pw * x4_pw
		t11 = a10 * x3_pw * x4_pw
	elif (conf[0][0] == 'x2'):
		t6 = a5 * x1_pw * np.power(x2, conf[0][1])
		t7 = a6 * x1_pw * x3_pw
		t8 = a7 * x1_pw * x4_pw
		t9 = a8 * np.power(x2, conf[0][1]) * x3_pw
		t10 = a9 * np.power(x2, conf[0][1]) * x4_pw
		t11 = a10 * x3_pw * x4_pw
	elif (conf[0][0] == 'x3'):
		t6 = a5 * x1_pw * x2_pw
		t7 = a6 * x1_pw * np.power(x3, conf[0][1])
		t8 = a7 * x1_pw * x4_pw
		t9 = a8 * x2_pw * np.power(x3, conf[0][1])
		t10 = a9 * x2_pw * x4_pw
		t11 = a10 * np.power(x3, conf[0][1]) * x4_pw
	else:
		t6 = a5 * x1_pw * x2_pw
		t7 = a6 * x1_pw * x3_pw
		t8 = a7 * x1_pw * np.power(x4, conf[0][1])
		t9 = a8 * x2_pw * x3_pw
		t10 = a9 * x2_pw * np.power(x4, conf[0][1])
		t11 = a10 * x3_pw * np.power(x4, conf[0][1])

	return t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11 + b0


# def predictor(x, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, b0, b1, b2):
# 	x1 = x[:,0]
# 	x2 = x[:,1]
# 	x3 = x[:,2]
# 	x4 = x[:,3]

# 	term1 = init_predictor(x, a0, a1, a2, a3, a4, a5, a6, b0)
# 	term2 = init_predictor(x, a7, a8, a9, a10, a11, a12, a13, b1)
# 	term3 = init_predictor(x, a14, a15, a16, a17, a18, a19, a20, b2)

# 	return term1 + np.multiply(x[:,4], term2) + 21 * term3
def predictor(x, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, \
	a20, a21, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31, a32, b0, b1, b2):
	x1 = x[:,0]
	x2 = x[:,1]
	x3 = x[:,2]
	x4 = x[:,3]

	term1 = init_predictor(x, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, b0)
	term2 = init_predictor(x, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, b1)
	term3 = init_predictor(x, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31, a32, b2)

	return term1 + np.multiply(x[:,4], term2) + 21 * term3

def init_test(x, p):
	x1 = x[:,0]
	x2 = x[:,1]
	x3 = x[:,2]
	x4 = x[:,3]

	x1_pw = np.power(x1, conf[1][0])
	x2_pw = np.power(x2, conf[1][1])
	x3_pw = np.power(x3, conf[1][2])
	x4_pw = np.power(x4, conf[1][3])

	# Main term
	temp = np.log10(convert_to_var(x, conf[0][0]) + 1)
	t1 = p[0] * np.power(temp, conf[0][1])

	# Secondary terms
	t2 = p[1] * x1_pw
	t3 = p[2] * x2_pw
	t4 = p[3] * x3_pw
	t5 = p[4] * x4_pw

	# Correlation terms
	if (conf[0][0] == 'x1'):
		t6 = p[5] * np.power(x1, conf[0][1]) * x2_pw
		t7 = p[6] * np.power(x1, conf[0][1]) * x3_pw
		t8 = p[7] * np.power(x1, conf[0][1]) * x4_pw
		t9 = p[8] * x2_pw * x3_pw
		t10 = p[9] * x2_pw * x4_pw
		t11 = p[10] * x3_pw * x4_pw
	elif (conf[0][0] == 'x2'):
		t6 = p[5] * x1_pw * np.power(x2, conf[0][1])
		t7 = p[6] * x1_pw * x3_pw
		t8 = p[7] * x1_pw * x4_pw
		t9 = p[8] * np.power(x2, conf[0][1]) * x3_pw
		t10 = p[9] * np.power(x2, conf[0][1]) * x4_pw
		t11 = p[10] * x3_pw * x4_pw
	elif (conf[0][0] == 'x3'):
		t6 = p[5] * x1_pw * x2_pw
		t7 = p[6] * x1_pw * np.power(x3, conf[0][1])
		t8 = p[7] * x1_pw * x4_pw
		t9 = p[8] * x2_pw * np.power(x3, conf[0][1])
		t10 = p[9] * x2_pw * x4_pw
		t11 = p[10] * np.power(x3, conf[0][1]) * x4_pw
	else:
		t6 = p[5] * x1_pw * x2_pw
		t7 = p[6] * x1_pw * x3_pw
		t8 = p[7]* x1_pw * np.power(x4, conf[0][1])
		t9 = p[8] * x2_pw * x3_pw
		t10 = p[9] * x2_pw * np.power(x4, conf[0][1])
		t11 = p[10] * x3_pw * np.power(x4, conf[0][1])

	return t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11 + p[11]

# def test(x, p): 
# 	x1 = x[:,0]
# 	x2 = x[:,1]
# 	x3 = x[:,2]
# 	x4 = x[:,3]

# 	arg = [p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[21]]
# 	term1 = init_test(x, arg)

# 	arg = [p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[22]]
# 	term2 = init_test(x, arg)

# 	arg = [p[14], p[15], p[16], p[17], p[18], p[19], p[20], p[23]]
# 	term3 = init_test(x, arg)

# 	return term1 + np.multiply(x[:,4], term2) + 21 * term3

def test(x, p): 
	x1 = x[:,0]
	x2 = x[:,1]
	x3 = x[:,2]
	x4 = x[:,3]

	arg = [p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[33]]
	term1 = init_test(x, arg)

	arg = [p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18], p[19], p[20], p[21], p[34]]
	term2 = init_test(x, arg)

	arg = [p[22], p[23], p[24], p[25], p[26], p[27], p[28], p[29], p[30], p[31], p[32], p[35]]
	term3 = init_test(x, arg)

	return term1 + np.multiply(x[:,4], term2) + 21 * term3

def prepare_params(conf, params, str_params):
	# Secondary terms
	if (conf[1][0] == 0):
		params[str_params[0]].vary = False
		params[str_params[0]].value = 0
	if (conf[1][1] == 0):
		params[str_params[1]].vary = False
		params[str_params[1]].value = 0
	if (conf[1][2] == 0):
		params[str_params[2]].vary = False
		params[str_params[2]].value = 0
	if (conf[1][3] == 0):
		params[str_params[3]].vary = False
		params[str_params[3]].value = 0
	# Correlation terms
	if (conf[2][0] == 0 or conf[1][0] == 0 or conf[1][1] == 0):
		params[str_params[4]].vary = False
		params[str_params[4]].value = 0
	if (conf[2][1] == 0 or conf[1][0] == 0 or conf[1][2] == 0):
		params[str_params[5]].vary = False
		params[str_params[5]].value = 0
	if (conf[2][2] == 0 or conf[1][0] == 0 or conf[1][3] == 0):
		params[str_params[6]].vary = False
		params[str_params[6]].value = 0
	if (conf[2][3] == 0 or conf[1][1] == 0 or conf[1][2] == 0):
		params[str_params[7]].vary = False
		params[str_params[7]].value = 0
	if (conf[2][4] == 0 or conf[1][1] == 0 or conf[1][3] == 0):
		params[str_params[8]].vary = False
		params[str_params[8]].value = 0
	if (conf[2][5] == 0 or conf[1][2] == 0 or conf[1][3] == 0):
		params[str_params[9]].vary = False
		params[str_params[9]].value = 0

	return(params)

# ************************ Main code *****************************
# ****************************************************************
path_to_results = "/home/theovakalopoulos/Desktop/Diplomatiki/results/"

outputs_path = path_to_results + "test1" + "/outputs"
# plots_path = path_to_results + "test1" + "/plots/"

perf_counters_path = path_to_results + "perf_cnts_t1/outputs/"
series_list = ["500s_perf_counters.csv", "600s_perf_counters.csv"]

rem_points = []
inter_points = []
all_points = []

for series in series_list:
	perf_counters_file = perf_counters_path + series
	bench_list = []
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
		bench_list.append(int(tokens[0]))
		IPC_list.append(float(tokens[1]))
		MPKI_list.append(float(tokens[2]))
		TLB_list.append(float(tokens[3]))
		BW_list.append(float(tokens[4]))

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

	for i in range(0, len(bench_list)):
		rem_points.append([remote[i], MPKI_list[i], IPC_list[i], TLB_list[i], BW_list[i]])
		inter_points.append([interleave[i], MPKI_list[i], IPC_list[i], TLB_list[i], BW_list[i]])
		all_points.append([remote[i], MPKI_list[i], IPC_list[i], TLB_list[i], BW_list[i], 1])
		all_points.append([interleave[i], MPKI_list[i], IPC_list[i], TLB_list[i], BW_list[i], 0.5])

rem_points_file = path_to_results + "model/rem_points.csv"
inter_points_file = path_to_results + "model/inter_points.csv"
all_points_file = path_to_results + "model/all_points.csv"
prediction_file = path_to_results + "model/prediction.csv"
ranking_file = path_to_results + "model/ranking.csv"

# ********************************************************************************************
# ****************************** Uncomment to change files ***********************************

# with open(rem_points_file, mode='w') as rem_file:
# 	file_writer = csv.writer(rem_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	file_writer.writerows(rem_points)

# with open(inter_points_file, mode='w') as inter_file:
# 	file_writer = csv.writer(inter_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	file_writer.writerows(inter_points)

# with open(all_points_file, mode='w') as all_file:
# 	file_writer = csv.writer(all_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	file_writer.writerows(all_points)
# *********************************************************************************************

# ******************* Calculate prediction ********************
all_points_arr = np.array(all_points)
xdata = all_points_arr[:,1:]
ydata = all_points_arr[:,0]
# print(xdata)
# print(ydata)
# param, param_cov = curve_fit(predictor, xdata, ydata)
# print(param)
# prediction = test(xdata, param)
# print(prediction)
# print(r2_score(ydata, prediction))
# print(mean_absolute_error(ydata, prediction))
# pred_data = ydata - prediction
# print(pred_data)

# with open(prediction_file, mode='w') as pred_file:
# 	file_writer = csv.writer(pred_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	file_writer.writerows(map(lambda x: [x], prediction))


# Calculate prediction using cross validation technique
# xdata = all_points_arr[30:,1:]
# ydata = all_points_arr[30:,0]
# testx = all_points_arr[0:29,1:]
# testy = all_points_arr[0:29,0]
# param, param_cov = curve_fit(predictor, xdata, ydata)
# prediction = test(testx, param)
# r2 = r2_score(testy, prediction)
# mae = mean_absolute_error(testy, prediction)
# print(r2)
# print(mae)

# xdata = []
# ydata = []
# for i in range(0,123):
# 	if (i<=29):
# 		xdata[i] = all_points_arr[i,1:]
# 		ydata[i] = all_points_arr[i,0]
# 	elif (i>29 and i<60):
# 		continue
# 	else:
# 		xdata[i-30] = all_points_arr[i,1:]
# 		ydata[i-30] = all_points_arr[i,0]

# testx = all_points_arr[30:59,1:]
# testy = all_points_arr[30:59,0]
# param, param_cov = curve_fit(predictor, xdata, ydata)
# prediction = test(testx, param)
# r2 = r2 + r2_score(testy, prediction)
# mae = mae + mean_absolute_error(testy, prediction)


# xdata = []
# ydata = []
# for i in range(0,123):
# 	if (i<=59):
# 		xdata[i] = all_points_arr[i,1:]
# 		ydata[i] = all_points_arr[i,0]
# 	elif (i>59 and i<90):
# 		continue
# 	else:
# 		xdata[i-30] = all_points_arr[i,1:]
# 		ydata[i-30] = all_points_arr[i,0]

# testx = all_points_arr[60:89,1:]
# testy = all_points_arr[60:89,0]
# param, param_cov = curve_fit(predictor, xdata, ydata)
# prediction = test(testx, param)
# r2 = r2 + r2_score(testy, prediction)
# mae = mae + mean_absolute_error(testy, prediction)

# xdata = all_points_arr[0:89,1:]
# ydata = all_points_arr[0:89,0]
# testx = all_points_arr[90:,1:]
# testy = all_points_arr[90:,0]
# param, param_cov = curve_fit(predictor, xdata, ydata)
# prediction = test(testx, param)
# r2 = r2 + r2_score(testy, prediction)
# mae = mae + mean_absolute_error(testy, prediction)

# print(r2/4)
# print(mae/4)


# ***************** Calculate prediction using cross validation technique ******************
functions = function_generator()
print("Number of functions to train: ", len(functions))

ranking = []
cnt = 0
err_cnt = 0
model_init = Model(init_predictor)
model = Model(predictor)

functions = functions[10175500:]
for func in functions:
	cnt += 1
	conf = func
	if (limit_func(conf)):
		continue
	params = model_init.make_params(a0=1, a1=1, a2=1, a3=1, a4=1, a5=1, a6=1, a7=1, a8=1, a9=1, a10=1, b0=1)
	str_params = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10']
	params = prepare_params(conf, params, str_params)
	# conf = (('x1', -2.0, -2.0), (-1.0, -2.0, -2.0, 1.5))
	# print(conf)

	# param, param_cov = curve_fit(predictor, xdata, ydata)
	# prediction = test(xdata, param)
	# ranking.append((conf, r2_score(ydata, prediction)))

	groups = [np.array(rem_points), np.array(inter_points)]
	for points in groups:
		g1 = points[0:15,1:]
		g2 = points[16:31,1:]
		g3 = points[32:47,1:]
		g4 = points[48:61,1:]

		y1 = points[0:15,0]
		y2 = points[16:31,0]
		y3 = points[32:47,0]
		y4 = points[48:61,0]

		sum_r2 = 0
		sum_mae = 0
		
		try:
			xdata = np.concatenate((g1,g2,g3), axis=0)
			ydata = np.concatenate((y1,y2,y3), axis=0)
			result = model_init.fit(ydata, params, x=xdata)
			param = list(result.params.valuesdict().values())
			prediction = init_test(g4, param)
			sum_r2 += r2_score(y4, prediction)
			sum_mae += mean_absolute_error(y4, prediction)

			xdata = np.concatenate((g2,g3,g4), axis=0)
			ydata = np.concatenate((y2,y3,y4), axis=0)
			result = model_init.fit(ydata, params, x=xdata)
			param = list(result.params.valuesdict().values())
			prediction = init_test(g1, param)
			sum_r2 += r2_score(y1, prediction)
			sum_mae += mean_absolute_error(y1, prediction)

			xdata = np.concatenate((g1,g2,g4), axis=0)
			ydata = np.concatenate((y1,y2,y4), axis=0)
			result = model_init.fit(ydata, params, x=xdata)
			param = list(result.params.valuesdict().values())
			prediction = init_test(g3, param)
			sum_r2 += r2_score(y3, prediction)
			sum_mae += mean_absolute_error(y3, prediction)

			xdata = np.concatenate((g1,g3,g4), axis=0)
			ydata = np.concatenate((y1,y3,y4), axis=0)
			result = model_init.fit(ydata, params, x=xdata)
			param = list(result.params.valuesdict().values())
			prediction = init_test(g2, param)
			sum_r2 += r2_score(y2, prediction)
			sum_mae += mean_absolute_error(y2, prediction)

			ranking.append((conf, sum_r2/4))

		except RuntimeError as e:
			err_cnt += 1
			continue

	if (cnt % 100 == 0):
		print("Maximum r2 socre so far: ", max(ranking, key=itemgetter(1))[1])
		print("Optimal function so far: ", max(ranking, key=itemgetter(1))[0])
		print("Errors so far: ", err_cnt)
		print(cnt, " out of ", len(functions), " checked.\n")

# print(max(ranking))
with open(ranking_file, mode='w') as rank_file:
	file_writer = csv.writer(rank_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	file_writer.writerows(ranking)

# # ***** Test the optimal function ******
# # **************************************
# conf = (('x2', 2.0), (1.5, -2.0, -1.5, 1.0), (1, 1, 1, 0, 0, 0))
# params = model.make_params(a0=1, a1=1, a2=1, a3=1, a4=1, a5=1, a6=1, a7=1, a8=1, a9=1, a10=1, b0=1, \
# a11=1, a12=1, a13=1, a14=1, a15=1, a16=1, a17=1, a18=1, a19=1, a20=1, a21=1, b1=1, \
# a22=1, a23=1, a24=1, a25=1, a26=1, a27=1, a28=1, a29=1, a30=1, a31=1, a32=1, b2=1)

# str_params = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10']
# params = prepare_params(conf, params, str_params)

# str_params = ['a12', 'a13', 'a14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20', 'a21']
# params = prepare_params(conf, params, str_params)

# str_params = ['a23', 'a24', 'a25', 'a26', 'a27', 'a28', 'a29', 'a30', 'a31', 'a32']
# params = prepare_params(conf, params, str_params)

# result = model.fit(ydata, params, x=xdata)
# param = list(result.params.valuesdict().values())
# prediction = test(xdata, param)
# print(r2_score(ydata, prediction))
# print(mean_absolute_error(ydata, prediction))
# with open(prediction_file, mode='w') as pred_file:
# 	file_writer = csv.writer(pred_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# 	file_writer.writerows(map(lambda x: [x], prediction))

# ******** New method for curve fit ********
# g1 = np.array(rem_points)[0:15,1:]
# g2 = np.array(rem_points)[16:31,1:]
# g3 = np.array(rem_points)[32:47,1:]
# g4 = np.array(rem_points)[48:61,1:]

# y1 = np.array(rem_points)[0:15,0]
# y2 = np.array(rem_points)[16:31,0]
# y3 = np.array(rem_points)[32:47,0]
# y4 = np.array(rem_points)[48:61,0]

# conf = (('x1', -2.0, -2.0), (-1.0, -2.0, -2.0, 1.5))
# xdata = np.concatenate((g1,g2,g3), axis=0)
# ydata = np.concatenate((y1,y2,y3), axis=0)
# param, param_cov = curve_fit(init_predictor, xdata, ydata)
# prediction = init_test(g4, param)
# print(param)
# print(r2_score(y4, prediction))
# print(mean_absolute_error(y4, prediction))

# result = model_init.fit(ydata, params, x=xdata)
# res = list(result.params.valuesdict().values())
# print(res)