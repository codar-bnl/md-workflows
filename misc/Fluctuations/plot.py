import numpy as np
import matplotlib.pyplot as plt


def scatterPlot(data):
	x = np.arange(1, 101)
	y = 20 + 3 * x + np.random.normal(0, 60, 100)
	return plt.plot([x,x], [y,y], "o")

def barChart():
	x = np.array([0,2,3])
	y = np.array([20,22,23])
	my_xticks = ['John','Arnold','Mavis','Matt']
	plt.xticks(x, my_xticks)
	plt.plot(x, y)
	plt.show()



