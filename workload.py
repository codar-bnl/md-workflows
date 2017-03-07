import radical.utils as ru
import CUDef 
def createWorkload(inputFile):
	'''
	Creates a workload composed of as many pipelines as they are specified in inputFile. Each pipeline is composed of a set of stages that correspond to bag of tasks. The ith stage of the jth pipeline contains a number of tasks equal to the entry (j,y) in the matrix specified in inputFile
	'''
	workloadDesc = ru.read_json(inputFile)
	workload = []
	totNumCUs = 0
	for pipeline in workloadDesc:
		stageList = []
		workload.append(stageList)
		for bof in pipeline:
			taskList = []
			stageList.append(taskList)
			totNumCUs += bof
			for i in range(0,bof):
				#cud = CUDef.createGromacsCU(1) ## The number of cores per CU has been set to 1. (hard coded, can be changed). The creation of the CU could stay outside the loop since all the CUs are the same
            			cud = CUDef.createDateCU() ## Create a /bin/date CU --- Comment the line above and de-comment this one if you want to try /bin/date
				taskList.append(cud)
	return (workload,totNumCUs)

