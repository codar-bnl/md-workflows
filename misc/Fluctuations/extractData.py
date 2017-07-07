import os

'''
Create a file with all the experiments that are contained in indir
outputName - Name of the output file
indir - Folder that contains the experiments
'''
def collectData(outputName,indir,nameLog = "info"):
	outputFile  = open(outputName,"w+")
	# Scroll all the experiments inside indir
	for dir in os.listdir(indir):
        	currSourceDir = indir + "/"+dir
        	# Scroll all the ranks within the experiments
        	for expDir in os.listdir(currSourceDir):
			currSourceDir+="/"+expDir
       			outputFile.write(dir +  " " + expDir + " ")
			if os.path.isfile(currSourceDir+"/"+ nameLog):
				infoFile = open(currSourceDir+"/"+nameLog)	
				for line in infoFile:
					outputFile.write(line[0:-1]+ " ")		
			else:
				outputFile.write("-")	
			outputFile.write("\n")
                ##Reset the path to one level below
                	currSourceDir = indir + "/"+dir        
	outputFile.close() 
'''
Read a file and put the data in memory. The data is organized in a hierarchy that follows the list groupBy.
dataIndex - index of the column from each the data is extracted
groupBy - List containing the indexes of the column used to create the hierachy

TODO : Comment this method properly

'''	
def readFileAndGroupBy(inputName,groupBy,dataCol,dataIsNum,separator = " "):		
	inputFile = open(inputName)
	data = {}
	length = len(groupBy)
	# Read all the lines
	for line in inputFile:
		tokens  = line.split(separator)
		if len(tokens) > 3:
			#Set the cursor to the root of the hieararchy
			cursor = data
			# Scroll all the hiearchy 
			for col in range(0,length):
				key = tokens[groupBy[col]]
				# If a branch has not been created yet then create it
			 	if not (key in cursor):
					if col == length-1:
						# Leaves are lists
						cursor[key]=[]
						for dataIndex in dataCol:
							cursor[key].append([]) 
					else: # If is not a leaf then it is dictionary
						cursor[key]={}
				cursor = cursor[key]
			#Append the data to the list on the leaf
			counter =0
			
			for dataIndex in dataCol:
			#print(str(len(tokens)) +  " "+str(dataIndex))
				item = tokens[dataIndex]
				if dataIsNum[counter]:
					item = float(item)
					
				cursor[counter].append(item)
				counter+=1	
	return data

