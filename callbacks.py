import time
import threading
import CUDef
import radical.pilot as rp
LOCK_LABEL = "lock" # Label of the shared lock in cb_data
MAP_LABEL = "map" # Label of the Hashmap in cb_data
WL_LABEL = "workload" #Label for the workload in cb_data
UM_LABEL = "umgr" # Label for the unit manager in cb_data
REPORT_LABEL = "report" # Label for the report in cb_data
CURR_LABEL = "status" # Label for the current status of the pipeline in cb_data
COUNTER_LABEL = "counter" # Label for the counter in cb_data
def catchTermination(unit,state, cb_data):
	'''
	Defines a method that catch the termination of a units and, if the stage is completed, sends the next state of the pipeline for execution
	'''
	if state == rp.DONE:
		cb_data[COUNTER_LABEL]-=1
		map = cb_data[MAP_LABEL]
		indexPipeline = map[unit.uid]
		pipeline = cb_data[WL_LABEL][indexPipeline]
		del map[unit.uid]
		#with cb_data[LOCK_LABEL]:
		del pipeline[0][0] # Pop of a CU from the current stage of the pipeline. Note that the stage is used as a counter. Information about the CUs in the current stage is not needed  after they are sent for execution. Thus the CU does not necessarily corresponds to the one completed.
		#print(" "+ str(len(pipeline[0])) + " " + str(map[unit.uid]))
		if(len(pipeline[0])==0):
			del pipeline[0] # Remove the current stage of the pipeline 
			if(len(pipeline) !=0): # If there is another stage then send it for execution
				cb_data[CURR_LABEL][indexPipeline]+=1
				cb_data[REPORT_LABEL].plain("Sending stage " + str(cb_data[CURR_LABEL][indexPipeline]) + "of pipeline "+ str(indexPipeline+1) + " for execution")
				units = cb_data[UM_LABEL].submit_units(pipeline[0])
				for item in units:
                     			map[item.uid] = indexPipeline

def generateDataTermination(lock,map,workload,umgr,report,numCUs):
	'''
	Inizialize the data sharing object required by the function catchTermination
	'''
	currentStages = [1]*len(workload)
	data={LOCK_LABEL: lock, 
	MAP_LABEL: map, 
	WL_LABEL : workload, 
	UM_LABEL :umgr,
	REPORT_LABEL : report,
	CURR_LABEL : currentStages,	 		
	COUNTER_LABEL : numCUs
	}
	return data 

def waitCUs(monitor):
	'''
	Wait Until the CUs counter in monitorp[COUNTER_LABEL] goes to zero
	'''
	while monitor[COUNTER_LABEL] !=0:
                monitor[REPORT_LABEL].plain("# of remaining CUs: " + str(monitor[COUNTER_LABEL]))
                time.sleep(10)                           
	monitor[REPORT_LABEL].info("All the CUs have been completed")
