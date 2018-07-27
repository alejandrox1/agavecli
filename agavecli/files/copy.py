"""
    copy.py
"""
from __future__ import print_function                                           
import json                                                                     
import requests                                                                 
import shutil
import sys                                                                      
import tempfile
from os import path
from ..utils import get_access_token, get_agave_context, handle_bad_response_status_code



def cp_local_to_remote(origin, destination, tenant_url, headers, params):
    """ Copy a file from local filesystem to remote Agave system
    """
    # Make sure the format for "origin" and "destination" is correct.
    if "agave://" not in origin[:8] and "agave://" in destination[:8]:
        pass
    else:
        print("Requesting wrong copy operation (local to remote agave system)", 
                file=sys.stderr)
        sys.exit(1)
    
    # Make request.
    try:
        agave_system = destination[8:] # Remove "agave://"
        
        # Prep request.
        files    = {"fileToUpload": open(origin, "rb")}
        endpoint = "{0}/{1}".format(tenant_url, agave_system)
        resp = requests.post(endpoint, files=files, headers=headers, params=params)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.                                               
    handle_bad_response_status_code(resp)

    return resp



def cp_remote_to_local(origin, destination, tenant_url, headers, params):
    """ Copy a file from remote Agave system to local filesystem
    """
    if "agave://" in origin[:8] and "agave://" not in destination[:8]:
        pass
    else:
        print("Requesting wrong copy operation (remote agave system to local)",
                file=sys.stderr)
        sys.exit(1)

    # Make request.
    try:
        agave_system   = origin[8:] # Remove "agave://"
        local_filename = destination.split('/')[-1]
        
        endpoint = "{0}/{1}".format(tenant_url, agave_system)
        resp = requests.get(endpoint, headers=headers, params=params, stream=True)
        with open(local_filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.                                               
    handle_bad_response_status_code(resp)

    return resp



def cp_remote_to_remote(origin, destination, tenant_url, headers, params):
    """ Copy a file from a remote Agave system to another
    """
    if "agave://" in origin[:8] and "agave://" in destination[:8]:
        pass
    else:
        print("Requesting wrong copy operation (remote agave system to remote)",
                file=sys.stderr)
        sys.exit(1)

    try:
        # Download file (stream it).
        origin_system      = origin[8:]      # Remove "agave://"
        destination_system = destination[8:] # Remove "agave://"
            
        origin_endpoint = "{0}/{1}".format(tenant_url, origin_system)
        resp = requests.get(origin_endpoint, headers=headers, params=params, stream=True)

        # Handle bad status code.
        handle_bad_response_status_code(resp)

        try:
            # Write downloaded file to /tmp/?
            tmpdir = tempfile.mkdtemp()
            filename = destination.split("/")[-1]
            if filename == "": filename = origin.split("/")[-1]
            filepath = path.join(tmpdir, filename)
            with open(filepath, "wb") as tmp:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        tmp.write(chunk)

            # Upload file from /tmp/? to remote system.
            destination_endpoint = "{0}/{1}".format(tenant_url, destination_system)
            files                = {"fileToUpload": open(filepath, "rb")}
            resp = requests.post(destination_endpoint, files=files, headers=headers, params=params)
        finally:
            shutil.rmtree(tmpdir)

        # Handle bad status code.
        handle_bad_response_status_code(resp)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)



def files_copy(agavedb, token_endpoint, endpoint, origin, destination):
    """ Copy files via the Agave API
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)
    
    # Get access token from agave database.
    access_token = get_access_token(agavedb, token_endpoint)
  
    headers    = {"Authorization":"Bearer {0}".format(access_token)}
    params     = {"pretty": "true"}
    tenant_url = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
    # cp local -> remote.
    if "agave://" not in origin[:8] and "agave://" in destination[:8]:
        # Copy file from local system to remote Agave system.
        resp = cp_local_to_remote(origin, destination, tenant_url, headers, params)
        
    # cp remote -> local.
    elif "agave://" in origin[:8] and "agave://" not in destination[:8]:
        # Copy file from remote Agave system to local file system.
        resp = cp_remote_to_local(origin, destination, tenant_url, headers, params)
    
    # cp remote -> remote
    elif "agave://" in origin[:8] and "agave://" in destination[:8]:
        # Copy file from a remote agave system to another.
        cp_remote_to_remote(origin, destination, tenant_url, headers, params)
