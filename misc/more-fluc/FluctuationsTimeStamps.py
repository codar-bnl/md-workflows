import glob
import math
import numpy as np
import math
import time
import sys
def loadData(filePath):
	inputFile = open(filePath)
	data = []
	for line in inputFile:
		tokens = line.split(' ')
		counter=0
		#print(filePath +" # tokens" + str(len(tokens)))
		if len(tokens) == 4:
			data.append(tokens)
	return data


def extractTimes(mult):
	data = {}
	for fileName in glob.glob("*.csv"):
		dataset = loadData(fileName)
		#print(len(dataset))
		acc = 0
		counter = 0	      
		for item in dataset:
			if item[2] != "":			
				acc+=float(item[2])
				counter+=1
		avg = acc/counter
		for item in dataset:
			if item[2] != "" and (mult*avg <= float(item[2])):
				data[item[1]] = True
				#print(fileName +  " " + str(avg*mult) +  " " + str(item[2])) 
	return data

def convertTimes(data,outputFileName):
	outfile = open(outputFileName,'w+')
	for key in data.keys():
		print(key)		
		outfile.write(time.strftime("%D-%H:%M", time.localtime(float(key)))+"\n")
	outfile.close()	

mult = float(sys.argv[1])
outputFileName = "DataPoint-"+str(mult)
data=extractTimes(mult)
convertTimes(data,outputFileName)
