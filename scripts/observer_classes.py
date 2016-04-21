# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 17:45:18 2016

@author: robouser
"""
import utilities
from datetime import datetime, timedelta
import json
from os import path
import urllib
import httplib

############################################################################
#                           EVENT OBSERVER CLASSES
############################################################################

class ObsRequest:
    
    def __init__(self, params=None):
        self.name = None
        self.ra = None
        self.dec = None
        self.get_new_group_id()
        self.jur = None
        
        if params != None:
            self.name = params['name']
            coords = ( params['ra'], params['dec'] )
            (self.ra, self.dec) = utilities.convert_sexig2dec( coords )
    
    def get_new_group_id(self):
        tnow = datetime.utcnow()
        time = float(tnow.hour) + (float(tnow.minute)/60.0) + \
                (float(tnow.second)/3600.0) + (float(tnow.microsecond)/3600e6)
        time = str( round(time,8) )
        date = tnow.strftime('%Y%m%d')
        
        self.group_id = 'RBN' + date + 'T' + time
    
    def build_request(self, sequence):
        """Function to build an observing Request from a pre-defined 
        sequence
        
        sequence is a list of dictionaries:
            { 
            tel_class: ['1m0', '2m0', '0m4'], 
            operation: [ 'single', 'many' ],
            start_datetime: %Y-%m-%dT%H:%M:%S
            stop_datetime: %Y-%m-%dT%H:%M:%S
            obs_type: [ 'NORMAL', 'TOO' ]
            }
        """
        
        location = { 'telescope_class': str( sequence['tel_class'] ) }
        target = {
                'name': self.name, \
                'ra': self.ra, \
                'dec': self.dec, \
                'proper_motion_ra': 0, \
                'proper_motion_dec': 0,\
                'parallax': 0,\
                'epoch': 2000
                }
        constraints = { 'max_airmass': 2.0 }
        
        if sequence['operator'] == 'single':
            
            windows = [ { 'start': sequence['start_datetime'].strftime('%Y-%m-%d %H:%M:%S'), \
                          'end': sequence['stop_datetime'].strftime('%Y-%m-%d %H:%M:%S')
                      } ]
                      
            molecule_list = []
            for i,f in enumerate( sequence['filters'] ):
                exptime = sequence['exptimes'][i]
                nexp = sequence['nexp'][i]
                
                mol =  {
                        'exposure_time': exptime,\
                        'exposure_count': nexp, \
                        'filter': f, \
                        'type': 'EXPOSE', \
                        'ag_name': '', \
                        'ag_mode': 'Optional', \
                        'instrument_name': str(sequence['instrument']).upper(),\
                        'bin_x': sequence['binning'],\
                        'bin_y': sequence['binning'],\
                        'defocus': 0.0
                        }
                molecule_list.append( mol )
            req_list = [ { 'observation_note': '', 
                          'observation_type': str(sequence['obs_type']).upper(),
                          'target': target, 
                          'windows': windows,
                          'fail_count': 0,
                          'location': location,
                          'molecules': molecule_list,
                          'type': 'request', 
                          'constraints': constraints
                          } ]

        else:
            t_start = sequence['start_datetime']
            t_end = sequence['stop_datetime']
            req_list = []
            request_start = t_start
            i = -1
            while request_start < t_end:
                i = i + 1
                molecule_list = []
                if i < len(sequence['window']):
                    obs_window = float(sequence['window'][i]) * 60.0 * 60.0
                    cadence = float(sequence['cadence'][i]) * 60.0 * 60.0
                else:
                    obs_window = float(sequence['window'][-1]) * 60.0 * 60.0
                    cadence = float(sequence['cadence'][-1]) * 60.0 * 60.0
                    
                request_end = request_start + timedelta(seconds=obs_window)
                if request_end < t_end:
                    for j,f in enumerate( sequence['filters'] ):
                        exptime = sequence['exptimes'][j]
                        nexp = sequence['nexp'][j]
                        
                        mol =  {
                                'exposure_time': exptime,\
                                'exposure_count': nexp, \
                                'filter': f, \
                                'type': 'EXPOSE', \
                                'ag_name': '', \
                                'ag_mode': 'Optional', \
                                'instrument_name': str(sequence['instrument']).upper(),\
                                'bin_x': sequence['binning'],\
                                'bin_y': sequence['binning'],\
                                'defocus': 0.0
                                }
                        molecule_list.append( mol )
                    
                    window = [ {  'start': request_start.strftime('%Y-%m-%d %H:%M:%S'), \
                                  'end': request_end.strftime('%Y-%m-%d %H:%M:%S')
                            } ]
                    req = { 'observation_note': '', 
                          'observation_type': str(sequence['obs_type']).upper(),
                          'target': target, 
                          'windows': window,
                          'fail_count': 0,
                          'location': location,
                          'molecules': molecule_list,
                          'type': 'request', 
                          'constraints': constraints
                          } 
                    req_list.append(req)
                request_start = request_start + timedelta( seconds=cadence )
            
            

        # Bring all the elements together to complete the request, 
        # and turn it into the required json format:
        ur = { 'group_id': self.group_id, 'operator': sequence['operator'] }
        ur['requests'] = req_list
        ur['type'] = 'compound_request'
        #print 'UR = ',ur, self.group_id
        
        
        self.jur = json.dumps(ur)
            
    def get_observer_params(self,obs_type):
        
        if obs_type == 'TARGET_OF_OPPORTUNITY':
            observer_file = path.join( path.expanduser('~'), '.obscontrol', \
                                        'observer.params.too' )
        else:
            observer_file = path.join( path.expanduser('~'), '.obscontrol', \
                                        'observer.params' )
        params = { 'username': None, 'password': None, 'proposal': None }        
        if path.isfile( observer_file ) == False:
            msg = 'ERROR: No observer authentication, cannot submit observation requests'
        else:
            file_lines = open(observer_file,'r').readlines()
            for line in file_lines:
                if line[0:1] != '#' and len(line.replace('\n','')) > 0:
                    (key,value) = line.replace('\n','').split()
                    if key in params.keys():
                        params[key] = value
        if None in params.values():
            msg = 'ERROR: Observer information incomplete, cannot submit observation requests'
        else:
            msg = 'OK'
        return msg, params
        
    def submit_request(self,obs_type,simulate=True):
        
        (msg,params) = self.get_observer_params(obs_type)
        
        if 'OK' in msg:
            if simulate == False:
                params['request_data'] = self.jur
                url = urllib.urlencode(params)
                hdr = {'Content-type': 'application/x-www-form-urlencoded'}
                
                secure_connect = httplib.HTTPSConnection("lcogt.net")
                secure_connect.request("POST","/observe/service/request/submit",url,hdr)
                submit_string = secure_connect.getresponse().read()
                submit_response = {}
                for entry in submit_string.replace('{','').replace('}','').replace('"','').split(','):
                    if 'Unauthorized' in entry:
                        msg = 'ERROR: ' + entry
                    elif 'time window' in submit_string:
                        msg = 'ERROR: ' + entry
                    else:
                        msg = 'Observations submitted ' + entry
                
                secure_connect.close()
            else:
                msg = 'SIMULATE: observation build successful'
        
        return msg
        
    