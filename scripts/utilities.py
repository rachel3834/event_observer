# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 18:22:24 2016

@author: robouser
"""

############################################################################
#                           UTILITIES
############################################################################

def convert_sexig2dec( coords ):
    """Function to convert a tuple of RA, Dec in sexigesimal format to decimal
    degrees"""
    
    ( ra_str, dec_str ) = coords
    
    ra_dec = sexig2dec( ra_str )
    ra_dec = ra_dec * 15.0
    
    dec_dec = sexig2dec( dec_str )
    
    return ra_dec, dec_dec
    
def sexig2dec(CoordStr):
    '''Function to convert a sexigesimal coordinate string into a decimal float, returning a value in
    the same units as the string passed to it.'''
    
    # Ensure that the string is separated by ':':
    CoordStr = CoordStr.lstrip().rstrip().replace(' ',':')
    
    # Strip the sign, if any, from the first character, making a note if its negative:
    if CoordStr[0:1] == '-':
        Sign = -1.0
        CoordStr = CoordStr[1:]
    else:
        Sign = 1.0
    
    # Split the CoordStr on the ':':
    CoordList = CoordStr.split(':')
    
    # Assuming this presents us with a 3-item list, the last two items of which will
    # be handled as minutes and seconds:
    try:
        Decimal = float(CoordList[0]) + (float(CoordList[1])/60.0) + (float(CoordList[2])/3600.0)
        Decimal = Sign*Decimal
    except:
        Decimal = 0
	
    # Return with the decimal float:
    return Decimal
