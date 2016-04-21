# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 17:31:49 2016

@author: robouser
"""

from os import path
from sys import argv, exit
import observer_classes
from datetime import datetime, timedelta

############################################################################
#                           EVENT OBSERVER
############################################################################

def observation_sequence( target_params, simulate=True, log=None ):
    """Function to submit a pre-set sequence of observations to the LCOGT
    network.
    Inputs:
        target_params  dictionary containing:
            { 'name': string target name, e.g. OGLE-2016-BLG-0001
              'ra': sexigesimal string, 
              'dec': sexigestimal string,
              'current_mag': float, best-available estimate of current magnitude
              'obs_sequence': string, name of pre-set observation sequence
            }
        
        Available observation sequences:
            'short-te': high cadence imaging in SDSS-i, Bessell-V over a 2day
                        period
    Outputs:
        submit_status dictionary of 
            obs_request_id: status_string
        for all requested observations
    """
    
    if log != None:
        log.write('Event Observer\n')
        log.write('  Triggering observation sequence with parameters: \n')
        for key, value in target_params.items():
            log.write('  '+str(key)+' = '+str(value)+'\n')
        log.write('  Simulate flag = ' + str(simulate)+' ' + \
                        str(type(simulate))+'\n')
        
    (status, sequence_list) = resolve_obs_sequence( target_params )
    if status == 'OK':
        submit_status = {}
        for sequence in sequence_list:
            obs_request = observer_classes.ObsRequest(params=target_params)
            obs_request.build_request( sequence )
            status = obs_request.submit_request(sequence['obs_type'], \
                                            simulate=simulate)
            submit_status[obs_request.group_id] = status
    else:
        submit_status = [ status ]
        
    return submit_status

def resolve_obs_sequence( target_params ):
    """Function to return the parameters of a pre-set observation sequence"""
    
    sequence_list = []
    # SHORT-TE CANDIDATE SEQUENCE
    # ToO: 4xSDSS-i, 4xBessell-V followed by
    # Queue: ( 4xSDSS-i, 4xBessell-V ) at an increasing cadence series
    if target_params['obs_sequence'] == 'short-te':
        tstart = datetime.utcnow() + timedelta(seconds=(5.0*60.0))
        tend = tstart + timedelta(seconds=(2.0*60.0*60.0))
        ToO = True
        if ToO == True:
            sequence1 = { 
            'tel_class': '1m0', 
            'operator': 'single',
            'start_datetime': tstart,
            'stop_datetime': tend,
            'obs_type': 'TARGET_OF_OPPORTUNITY',
            'instrument': '1M0-SCICAM-SBIG',
            'filters': [ 'ip', 'ip', 'V', 'V' ],
            'exptimes': [ 100.0, 300.0, 100.0, 300.0 ],
            'nexp': [ 1, 2, 1, 2 ],
            'binning': 2
            }
            sequence_list.append( sequence1 )
        tstart = datetime.utcnow() + timedelta(seconds=(5.0*60.0))
        tend = tstart + timedelta(seconds=(48.0*60.0*60.0))
        sequence2 = { 
            'tel_class': '1m0', 
            'operator': 'many',
            'start_datetime': tstart,
            'stop_datetime': tend,
            'obs_type': 'NORMAL',
            'instrument': '1M0-SCICAM-SBIG',
            'filters': [ 'ip', 'ip', 'V', 'V' ],
            'exptimes': [ 100.0, 300.0, 100.0, 300.0 ],
            'nexp': [ 1, 2, 1, 2 ],
            'binning': 2, 
            'cadence': [ 1.0, 1.0, 2.0, 3.0 ],
            'window':  [ 1.0, 1.0, 1.0, 1.0 ]
            }
        sequence_list.append( sequence2 )
        status = 'OK'
    else:
        status = 'ERROR: Unknown observation sequence requested'
        sequence_list = []

    return status, sequence_list


if __name__ == '__main__':
    simulate = False
    if len(argv) > 1:
        if 'simulate' in argv[1] and 'false' in argv[1]:
            simulate = False
    target_params = { 'name': 'OGLE-2016-BLG-0061', \
                      'ra': '17:54:23.71', \
                      'dec': '-29:05:20.2',
                      'obs_sequence': 'short-te'
                    }
    submit_status = observation_sequence( target_params, simulate=simulate )
    for id,msg in submit_status.items():
        print id, ': ', msg
    
