"""
    files.py
"""
from __future__ import print_function, division
import json
import os
import requests
import shutil
import sys
import time
from operator import itemgetter
from os import path
from ..utils import get_access_token, get_agave_context, handle_bad_response_status_code



file_permissions = {
    "READ"          : "-r--",
    "WRITE"         : "--w-",
    "EXECUTE"       : "---x",
    "READ_WRITE"    : "-rw-",
    "READ_EXECUTE"  : "-r-x",
    "WRITE_EXECUTE" : "--wx",
    "ALL"           : "-rwx",
    "NONE"          : "----"
}


def parse_agave_time(ftime):
    """ Convert timestamp from Agave to local time

    Expect format: 2018-07-10T12:28:01.000-05:00

    """
    # 2018-07-10T12:28:01.000-05:00 (rm last ':')
    if ftime[-3] == ":": ftime = ftime[:-3] + ftime[-2:]

    try:
        ftime = time.strptime(ftime,'%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        tz = ftime[-5:] # get the timezone part (i.e., -0500)
        ftime = time.strptime(ftime[:-5],'%Y-%m-%dT%H:%M:%S.%f')
        if tz.startswith("-"):
            sign = -1
            tz = tz[1:] # get the hous offset
        elif tz.startswith("+"):
            tz = tz[1:] # get the hous offset
        seconds = ( int(tz[0:2])*60 + int(tz[2:4]) ) * 60
        seconds *= sign
        # Convert ftime to seconds since epoch,
        ftime = time.mktime(ftime) + seconds
        # Convert seconds since epoch to localtime.
        ftime = time.localtime(ftime)

    outtime = time.strftime("%b %d %H:%M", ftime).split()

    return ftime, outtime




def files_list(agavedb, token_endpoint, endpoint, syspath, long_format=False):
    """ List files on a remote Agave system
    """
    # Open up the local agave database.
    agave_context = get_agave_context(agavedb)

    # Get access token from agave database.
    access_token = get_access_token(agavedb, token_endpoint)
    
    # Make request.                                                             
    try:
        endpoint = "{0}{1}/{2}".format(agave_context["current"]["baseurl"], endpoint, syspath)
        headers  = {"Authorization":"Bearer {0}".format(access_token)}
        params   = {"pretty": "true"}
        resp = requests.get(endpoint, headers=headers, params=params)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    
    # Handle bad status code.
    handle_bad_response_status_code(resp)


    # Sort results alphabetically.
    resp.json()["result"] = sorted(resp.json()["result"], key=itemgetter("name"), reverse=True)

    # Get the length of the longest filename.
    longest_name = 8
    for f in resp.json()["result"]:
        if len(f["name"]) > longest_name:
            longest_name = len(f["name"])
    largest_file = 0
    for f in resp.json()["result"]:
        if len(str(f["length"])) > largest_file:
            largest_file = len(str(f["length"]))

    # Get size of terminal.
    try: # python3 prefered
        terminal_size = shutil.get_terminal_size()
        terminal_size_columns = terminal_size.columns 
        columns = terminal_size.columns // longest_name
    except AttributeError:
        _rows, columns = os.popen('stty size', 'r').read().split()
        terminal_size_columns = int(columns)
        columns = int(columns) // longest_name

    if not long_format:
        files = ""
        line_length = 0
        for f in resp.json()["result"]:
            name   = f["name"]
            if f["type"] == "dir":
                name += "/"
            name += " " * (longest_name - len(name) + 3)

            if line_length + len(name) > terminal_size_columns:
                files += "\n"
                line_length = 0

            line_length += len(name)
            files += name

        print(files)
    else:
        for f in resp.json()["result"]:
            # File permissions and name.
            name   = f["name"]
            perm = file_permissions[f["permissions"]]
            if f["type"] == "dir":
                perm = "d{}".format(perm[1:])
                name += "/"
            name += " " * (longest_name - len(name) + 3)

            # File size.
            fsize = f["length"]

            # Date created.
            ftime, outtime = parse_agave_time( f["lastModified"] )

            print("{0:<4} {1:>{size_width}} {2:<3} {3:>2} {4:<5} {5:}".format(
                    perm, fsize, outtime[0], ftime.tm_mday, outtime[2], name, 
                    size_width=largest_file))



def files_remove(agavedb, token_endpoint, endpoint, syspath):
    """ Remove a file or direcotry from an Agave system
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)

    # Get access token from agave database.
    access_token = get_access_token(agavedb, token_endpoint)

    # Make request.
    try:
        endpoint = "{0}{1}/{2}".format(agave_context["current"]["baseurl"], endpoint, syspath)
        headers  = {"Authorization":"Bearer {0}".format(access_token)}
        params   = {"pretty": "true"}
        resp = requests.delete(endpoint, headers=headers, params=params)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    handle_bad_response_status_code(resp)
