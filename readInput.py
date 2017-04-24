import os
import sys
import radical.pilot as rp 
import os.path

# Name of the file that contains the environment variables necessary for the exectuion of Athena-MP
ENV_FILE="envFile"
#Name of the launcher
LAUNCHER = "launcher.sh"

def getPanDAJobExecutable(PanDAID):
	"""
	The method generates the name of the executable for the PandDA job
	PanDAID is the id of the job
	"""
	return("pj"+PanDAID+".sh")

def createLauncher(pathFile): 
	"""
	Generates the executable for launching of the ATHENA-MP. The launcher is a bash script that contains all the environment variables from ENV_FILE and runs the simulator. 
	
	"""
	executable = pathFile+"/"+LAUNCHER
	file = open(executable,"w+") # PanDAID is used to generate the name of the executable.
	file.write("#!/bin/bash\n")
	file.write("while read p; do export \"$p\"; done < "+pathFile+"/"+ ENV_FILE+"\n")
	#file.write("/bin/sh /lustre/atlas2/csc108/scratch/aleang9/radical.pilot.sandbox/nodelog.sh &\n")  # AM
	file.write("$1\n")
	file.close()
	os.chmod(executable,0777)



def setCUCommonPropertiesForOrte(newCommand,pathFile):
	"""
	Generates a cu to launch the simulation with ORTERUN. Set the executable, the eventFile and the file containing the environment as data staging.
	"""
	cud = rp.ComputeUnitDescription()
	cud.environment ={}
	cud.pre_exec = [
	"export ATHENA_PROC_NUMBER=16"
	#"mkdir poolcond",
	#"cp /lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/19.2.5/DBRelease/current/poolcond/*.xml  ./poolcond/.",
	#"export OMP_NUM_THREADS=16"
	]
	cud.post_exec=["rm -rf *"] # Comment this if the simulation is not for testing	
	#executable =getPanDAJobExecutable(PanDAID)
	cud.input_staging = [pathFile+"/"+LAUNCHER]
	cud.arguments = [newCommand]
	cud.executable = pathFile+"/"+LAUNCHER	
	cud.mpi = False
	cud.cores=16
	return cud
	
def setCUCommonPropertiesForAprun(PanDAID,newCommand,eventFileName):
	"""
	Generates a cu to launch the simulation with APRUN. Set the event file as data staging.
	ALERT : the executable is passed as argument because aprun needs a further parameter.
	"""
	cud = rp.ComputeUnitDescription()
	cud.environment ={}
	cud.pre_exec = [
	#"export tmp_dirname=$PBS_O_WORKDIR",
	#"export TEMP=$tmp_dirname",
        #"export TMPDIR=$TEMP",	
	"export LD_LIBRARY_PATH=/lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/19.2.5/ldpatch:$LD_LIBRARY_PATH",
	#"source /lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/19.2.5/AtlasSetup/scripts/asetup.sh 19.2.5.3,64,slc6,opt,gcc47 --cmtextratags=ATLAS,useDBRelease",
	"export CORAL_AUTH_PATH=/lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/orig_19.2.4/DBRelease/current/XMLConfig",
	"export CORAL_DBLOOKUP_PATH=/lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/orig_19.2.4/DBRelease/current/XMLConfig",
	"export DB_LOCATION=/lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/orig_19.2.4/DBRelease/current",
	"export CALIBPATH=$CALIBPATH:/lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/orig_19.2.4/DBRelease/current",
	"export ATHENA_PROC_NUMBER=16",
	#"mkdir poolcond",
	#"cp /lustre/atlas/proj-shared/csc108/app_dir/atlas_app/atlas_rel/19.2.5/DBRelease/current/poolcond/*.xml  ./poolcond/.",	
	]
	
	#cud.input_staging = [eventFileName]
	
	executable =getPanDAJobExecutable(PanDAID)
	cud.input_staging = [executable]
	cud.arguments=["16","./"+executable]
	cud.executable = "-d" #Trick to add a parameter to aprun
	cud.mpi = False
	cud.cores=16
	return cud	


def extractEventList(inputFile,pathFile,withOrte):
	""" 
	Takes in input a string that contains the path of ATLAS input file and returns a list of CUs
	WithOrte is a flag to discriminate between orterun or for aprun
	"""
	try:
		# Open the input file
		file = open(inputFile,"r+")
		# Each line contains the description of an event
		lines = file.read().splitlines()
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror)
    		print "Exiting wrapper...."
    		exit()
	return parseEachEvt(lines,pathFile,withOrte)

def parseEachEvt(eventList,pathFile,withOrte=False):
	"""
	Takes in input a list of strings; each string provides the parameters necessary for the execution of a simulation
	Returns a list of RP CUs that is described in terms of executable, data staging and pre-execution.
	withOrte is a flag to discriminate between orterun and aprun
	"""
	cudList = list()
	numEvtList = list()
	evtCounter = 0 # this counter substitutes ranks in Sergey's MPI  script
	if(not os.path.exists(pathFile+"./"+LAUNCHER)):
		createLauncher(pathFile)
	for eventString in eventList:
		temp = eventString.split("!!")  
		PanDAID = temp[0].replace(" ","") # Uses PanDA's jobID as name of the file 
		temp = temp[1].split() # Split the executable and all the arguments in different strings	
		newCommand = temp.pop(0) #New command string 
                # First element of the list is the executable. Therefore I remove it ----# it should be removed with aprun
                EventFileName = None
		for arg in temp :
		
			if "inputEVNTFile" in arg:
				(m_key,EventFileName) = arg.split("=")
        			#print m_key," ", EventFileName
				new_item = m_key+"=" + pathFile+"/" + EventFileName
				newCommand += " " + new_item
			elif '"' in arg:
        			arg = arg.replace('"','')
		                newCommand += " " + arg
			elif "maxEvents" in arg: # Otherwise concatenate the item as it is
			        (m_key,numEvt) = arg.split("=")
				numEvtList.append(int(numEvt))	
				newCommand+=" "+ arg	
			else : # Otherwise concatenate the item as it is
				newCommand+=" "+ arg
		#print "#PanDA Job:", evtCounter, " ", "New Command: ",newCommand
		#writePreExecOnFile(PanDAID,pathFile,newCommand)	
		if withOrte :
				
			cudList.append(setCUCommonPropertiesForOrte(newCommand,pathFile))
		else :
			cudList.append(setCUCommonPropertiesForAprun(PanDAID,newCommand,EventFileName))
		evtCounter+=1	
	return (cudList,numEvtList)			
