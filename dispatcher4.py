#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys
import threading
verbose  = os.environ.get('RADICAL_PILOT_VERBOSE', 'REPORT')
os.environ['RADICAL_PILOT_VERBOSE'] = verbose

import radical.pilot as rp
import radical.utils as ru
import callbacks
import CUDef 
import readInput
import json
import math

'''
The script executes the ATLAS workload on Oak ridge TITAN
Main receives in input the scheme to interact with TITAN and an input file that describe the ATLAS workload.
Methods are provided to parse the file.
'''
ARG_NUM = 3
OPT_FILE_INDEX =1
INPUT_FILE_INDEX =2

FACILITY_JSON_LABEL ="Facility" # Determines the entry of the config file --- Note that at the moment only the entries that refer to ORNL TITAN have been tested
PARALLEL_JSON_LABEL ="Parallel" # number of jobs that are executed simultaneously within the pilot
SEQUENTIAL_JSON_LABEL ="Sequential" # the number of jobs that are executed one after the other within the pilot  
ETEVT_JSON_LABEL ="ETPerEvent" # Estimate of the time required to complete a single event
ETSETUP_JSON_LABEL ="ETSetup" # Estimate of the time required to run to make Athena-MP start
MODE_JSON_LABEL="Mode" #Specify the job submission type -- How many pilots, how jobs are dispatched on the pilots,the queue and so on.
HOMO_JSON_MODE="Homogeneous" #All the jobs are considered equal as events
DEBUG_JSON_MODE ="Debug" # Set the debug mode --- Debug queue, 1 node for one hour
PATH_JSON_LABEL="PathFiles"# Set the path where the event files and envFile are
ORTE_LABEL = "ornl.titan"
MAXNUMSIM_JSON_LABEL = "maxNumSim" # Set a maximum number of simulation that will be considered for running

def createWorkload(options,config,withOrte,nodes,generations,seconds):
	resource = "ornl.titan_lib"
	cuList = []
	
	runtime = generations*seconds/60+20
	print(str(seconds)  +" " +  str(generations) + " "+ str(runtime))
	for i in range(0,nodes*generations*16):
		cuList+=[CUDef.createSleepCU(seconds)]
	print(len(cuList))
	pd_init = {
                	'resource'      : resource,
                	'runtime'       : runtime,  # pilot runtime (min)
                	'exit_on_error' : True,
               		'project'       : config[resource]['project'],
                	'queue'         : config[resource]['queue'],
                	'access_schema' : config[resource]['schema'],
                	'cores'         : 16*nnodes +16,# Additional 16 cores are for ORTE 
        	}
	
	pilots = []
	pilots.append(rp.ComputePilotDescription(pd_init))
	return (pilots,cuList)


if __name__ == '__main__':

#----------Argument Checking----------------------------------------------------- 
    # Exit if the script is executed with less than two arguments
    if len(sys.argv) < ARG_NUM : 
	print("At least one argument is missing")
	exit()
    report = ru.LogReporter(name='radical.pilot', level=verbose)
    report.title('Getting Started (RP version %s)' % rp.version)

    # read the config used for resource details
    report.info('read config')
    config = ru.read_json('%s/config.json' % os.path.dirname(os.path.abspath(__file__)))
    report.ok('>>ok\n')
    # read the options used for resource details
    report.info('Execution details config')
    report.ok('>>ok\n')
    #TO DO : This is sound only on TITAN -- It should be adjusted by building a set with all the entries of "config.json" that use ORTE
    withOrte = True
    nnodes = int(sys.argv[1])
    generations = int(sys.argv[2])
    seconds = int(sys.argv[3])
    options = ru.read_json("./runHomogeneous.json")
    (pilotDescList,cuList) = createWorkload(options,config,withOrte,nnodes,generations,seconds)

    
    

#-------------------------------------------------------------------------------

    # we use a reporter class for nicer output
    	# Create a workload of ComputeUnits. 

    

        # Create a new session. No need to try/except this: if session creation
    # fails, there is not much we can do anyways...
    session = rp.Session()
    reportfile = open("outputSleep-"+str(len(cuList))+"-"+str(nnodes)+"-"+str(session.uid),"w+")
    # all other pilot code is now tried/excepted.  If an exception is caught, we
    # can rely on the session object to exist and be valid, and we can thus tear
    # the whole RP stack down via a 'session.close()' call in the 'finally'
    # clause...
    try:

        # read the config used for resource details
        report.info('read config')
        config = ru.read_json('%s/config.json' % os.path.dirname(os.path.abspath(__file__)))
        report.ok('>>ok\n')

        report.header('submit pilots')

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        pmgr = rp.PilotManager(session=session)

		

        # Launch the pilot.
	pilots = []
        for pDesc in pilotDescList:
		pilots.append(pmgr.submit_pilots(pDesc))


        report.header('submit units')

        # Register the ComputePilot in a UnitManager object.
        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilots)
                # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        units = umgr.submit_units(cuList)
	# Register a callback for the resubmission of failed units --- Lock is there as a reminder, for the moment we are not using it.
	#lock = threading.Lock()
	#umgr.register_callback(callbacks.CollectFailedUnits, cb_data={callbacks.LOCK_LABEL: lock, callbacks.UMGR_LABEL: umgr,callbacks.FAILLIST_LABEL:[],'test':rp.FAILED})
        # Wait for all compute units to reach a final state (DONE, CANCELED or FAILED).
        report.header('gather results')
        umgr.wait_units()
    
        report.info('\n')
        for unit in units:
                reportfile.write(str(unit.uid) + " "+ str(unit.state) +" "+ str(unit.exit_code) + "\n") 
    
    	reportfile.close()
    except Exception as e:
        # Something unexpected happened in the pilot code above
        report.error('caught Exception: %s\n' % e)
        raise

    except (KeyboardInterrupt, SystemExit) as e:
        # the callback called sys.exit(), and we can here catch the
        # corresponding KeyboardInterrupt exception for shutdown.  We also catch
        # SystemExit (which gets raised if the main threads exits for some other
        # reason).
        report.warn('exit requested\n')

    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        report.header('finalize')
        session.close(cleanup=False) 
    CUDef.saveData("sandboxes",session.uid,"sleep")
    report.header()


#-------------------------------------------------------------------------------

