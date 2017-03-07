#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'
import callbacks
import os
import sys
import threading
import radical.pilot as rp
import radical.utils as ru
import CUDef
import workload as wl
import time
# ------------------------------------------------------------------------------
#
# READ the RADICAL-Pilot documentation: http://radicalpilot.readthedocs.org/
#
# ------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#
if __name__ == '__main__':

     
    # we use a reporter class for nicer output
    report = ru.LogReporter(name='radical.pilot')
    report.title('Getting Started (RP version %s)' % rp.version)
    # use the resource specified as argument, fall back to localhost
    resource = "local.localhost" # Type of resource
    numCUs=1 # Number of CUs
    workload = None # Initialize workload to give it a scope outside the if 
    numCores=128 # Number of cores
    if   len(sys.argv)  == 1: 
    	 (workload,numCUs) = wl.createWorkload("./workload.json") # Create the workload by using the default file
	 print("Default paramters: pipeline.json is used as input and it will run on 128 cores")
    elif len(sys.argv) ==3:  
   	(workload,numCUs) = wl.createWorkload(sys.argv[1]) # Creates the workload according the input file
	numCores= int(sys.argv[2]) # Number of cores
    else: 
	print("Help: python example.py <name input file>.json <# cores>")
	exit()
        if numCores > 128:
		print("This branch of Radical Pilot is still under testing. We recommend to use a number of cores smaller than 128")
		print("Comment lines 36-39 if you want to increase the number of cores")
		exit()
    if numCUs > 512 and numCores < 256:
		print("Alert: 120 miutes might not be enough to run 512 single thread gromacs simulation with less than 256 cores")
    # Create a new session. No need to try/except this: if session creation
    # fails, there is not much we can do anyways...
    session = rp.Session()
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

        # Define an [n]-core local pilot that runs for [x] minutes
        # Here we use a dict to initialize the description object
        pd_init = {
                'resource'      : resource,
                'runtime'       : 120,  # pilot runtime (min) Set as the maximum allowed in TITAN's fifth bin
                'exit_on_error' : True,
                'project'       : config[resource]['project'],
                'queue'         : config[resource]['queue'],
                'access_schema' : config[resource]['schema'],
                'cores'         : numCores+16, #An additional node must be reserved for ORTE
                }
        pdesc = rp.ComputePilotDescription(pd_init)

        # Launch the pilot.
        pilot = pmgr.submit_pilots(pdesc)


        report.header('submit units')

        # Register the ComputePilot in a UnitManager object.
        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        # Create a workload of ComputeUnits.
        # Each compute unit runs '/bin/date'.

        report.info('create '+str(numCUs) +'unit description(s)\n\t' )

        #Sends the first state of each pipeline for execution 
	
	map = {} # Create a hashMap to trace the units 	

	# Register a callback for the control of the pipelines of --- At the moment, a lock is required for preserving mutual exclusion of umgr.
        lock = threading.Lock()
        shareData = callbacks.generateDataTermination(lock,map,workload,umgr,report,numCUs)
	umgr.register_callback(callbacks.catchTermination, cb_data=shareData)
		
        
	for i in range(0, len(workload)):
		report.plain("Sending stage"+ str(1) +" of pipeline " + str(i) + " for execution")
 		units = umgr.submit_units(workload[i][0])	
		for unit in units:
			map[unit.uid] = i

        # Wait for all compute units to reach a final state (DONE, CANCELED or FAILED).
        #report.header('gather results')
    	#  Wait that all the CUs have been completed
	callbacks.waitCUs(shareData)
	
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
        session.close()

    report.header()


#-------------------------------------------------------------------------------

