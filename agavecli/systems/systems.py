"""
    systems.py
"""
from __future__ import print_function
import json
import requests
import sys
from os import path
from ..utils import get_access_token, get_agave_context, handle_bad_response_status_code



def system_list(agavedb, endpoint, token_endpoint, print_execution, print_storage):
    """ List all Agave systems available to the authenticated user
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)

    # Get access token from agave database.
    access_token = get_access_token(agavedb, token_endpoint)

    # Make request.                                                             
    try:
        headers  = {"Authorization":"Bearer {0}".format(access_token)}
        params   = {"pretty": "true"}
        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.get(endpoint, headers=headers, params=params)   
    except requests.exceptions.MissingSchema as err:                            
        print(err, file=sys.stderr)                                             
        sys.exit(1)                                                             
    
    # Handle bad status code.
    handle_bad_response_status_code(resp)

    # Print results.
    print("{0:<30} {1:<10} {2:<5} {3:<5}".format("ID", "TYPE", "DEFAULT", "PUBLIC"))
    for system in resp.json()["result"]:
        sys_type = system["type"].lower()
        default  = "Y" if system["default"] else "N"
        public   = "Y" if system["public"] else "N"

        if print_execution and sys_type == "execution":
            print("{0:<30} {1:<10} {2:<5} {3:<5}".format(system["id"], sys_type, default, public))
        elif print_storage and sys_type == "storage":
            print("{0:<30} {1:<10} {2:<5} {3:<5}".format(system["id"], sys_type, default, public))
        elif not print_execution and not print_storage:
            print("{0:<30} {1:<10} {2:<5} {3:<5}".format(system["id"], sys_type, default, public))
