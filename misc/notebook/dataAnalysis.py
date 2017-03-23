def loadData(filePath,cols):
	inputFile = open(filePath)
	inputFile.readline() #consume line
	data = []
	size = len(cols)
	for i in range(0,size):
		data.append([])
	for line in inputFile:
		tokens = line.split(',')
		counter=0
		for i in cols:
			data[counter].append(tokens[i])
			counter+=1
	return data
