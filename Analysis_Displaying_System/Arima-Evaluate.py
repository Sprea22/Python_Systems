import warnings
import sys
import os
import numpy as np
import pandas as pd
from pandas import Series
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error


def mean_absolute_percentage_error(y_true, y_pred): 
	rng = len(y_true)
	diff = []
	for i in range(0,rng):
		diff.append(y_true[i] - y_pred[i])
		diff[i] = diff[i] / y_true[i]
	abs = np.abs(diff)
	mn = np.mean(abs)
	percentageError = mn * 100
	return percentageError
    
# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(X, arima_order):
	# prepare training dataset
	train_size = int(len(X) * 0.66)
	train, test = X[0:train_size], X[train_size:]
	history = [x for x in train]
	# make predictions
	predictions = list()
	for t in range(len(test)):
		model = ARIMA(history, order=arima_order)
		model_fit = model.fit(disp=0)
		yhat = model_fit.forecast()[0]
		predictions.append(yhat)
		history.append(test[t])
	# calculate out of sample error
	error = mean_absolute_percentage_error(test, predictions)
	return error

# evaluate combinations of p, d and q values for an ARIMA model
def evaluate_models(dataset, p_values, d_values, q_values):
	dataset = dataset.astype('float32')
	best_score, best_cfg = float("inf"), None
	filename = "Results/"+sys.argv[1]+"/"+sys.argv[2]+"/"+"Predictions/MAPE.csv"
	if not os.path.exists(os.path.dirname(filename)):	
		os.makedirs(os.path.dirname(filename))

	with open(filename, "w") as myfile:
		myfile.write("P, D, Q, MAPE\n")
	for p in p_values:
		for d in d_values:
			for q in q_values:
				order = (p,d,q)
				try:
					mape = evaluate_arima_model(dataset, order)

					if mape < best_score:
						with open(filename, "a") as myfile:
							myfile.write('%d, %d, %d, %.3f%% \n' % (p,d,q,mape))
						best_score, best_cfg = mape, order
					print('ARIMA%s MAPE=%.3f%%' % (order,mape))
				except:
					print('ARIMA%s MAPE=Nil' % str(order))
					continue
	print('Best ARIMA%s MAPE=%.3f%%' % (best_cfg, best_score))

# load dataset
series = pd.read_csv("Datasets/"+sys.argv[1]+".csv", header=0, usecols=[sys.argv[2]])
# evaluate parameters
p_values = [0, 1, 2, 4, 6, 8, 10]
d_values = [0,1,2,3]
q_values = [0,1,2,3]
warnings.filterwarnings("ignore")
evaluate_models(series.values, p_values, d_values, q_values)