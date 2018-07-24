"""
    directories.py
"""
from __future__ import print_function
import json
import requests
import sys
from os import path
from ..utils import get_access_token, get_agave_context, handle_bad_response_status_code



def files_mkdir(agavedb, token_endpoint, endpoint, syspath):
    """ Make directries on a remote Agave system
    """
    # Get baseurl for tenant.                                                   
    agave_context = get_agave_context(agavedb)
    
    # Get access token from agave database.                                     
    access_token = get_access_token(agavedb, token_endpoint)
    
    # Make request.                                                             
    try:
        # Get system name and path of directory to make.
        syspath      = syspath.split("/")
        agave_system = syspath[0]
        dir_path     = "/".join( syspath[1:] )

        # Prep request.
        endpoint = "{0}{1}/{2}".format(agave_context["current"]["baseurl"], endpoint, agave_system)
        headers  = {"Authorization":"Bearer {0}".format(access_token)}
        data     = {"action": "mkdir", "path": dir_path}
        params   = {"pretty": "true"}
        resp = requests.put(endpoint, data=data, headers=headers, params=params)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    
    # Handle bad status code.
    handle_bad_response_status_code(resp)
