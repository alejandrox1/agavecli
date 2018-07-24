"""
    agavedb.py
"""
from __future__ import print_function                                           
import getpass                                                                  
import json                                                                     
import requests                                                                 
import sys                                                                      
import time                                                                     
from os import path                                                             
from .response_handlers import handle_bad_response_status_code



def get_agave_context(agavedb):
    """ Get the current Agave context

    Look for the local Agave database and return a reference to it.

    INPUTS
    ------
    agavedb : str
        Directory localtion of the local Agave database (dedault usage: ~/).

    RETURNS
    -------
    agave_context : dict
        Dictionary with all usage pertaining to the current user's session.
    """
    agavedb = "{}/agave.json".format(agavedb)
    if path.isfile(agavedb):
        with open(agavedb, "r") as f:
            agave_context = json.load(f)
    else:
        print("Please specify an Agave tenant to interact with before trying to create a client",
                file=sys.stderr)
        sys.exit(1)

    return agave_context


def get_access_token(agavedb, token_endpoint):
    """ Get the Access Token
    
    Return the access token contained in the local agave database or refresh it
    if expired.

    INPUTS
    ------
    agavedb : str
        Directory localtion of the local Agave database (dedault usage: ~/)
    token_endpoint : str
        Token service endpoint for agave (defualts to: token).
    agave_context : dict
        Dictionary representing the user's local agave database.

    RETURNS
    -------
    access_token : str
    """
    # Check if access token needs to be refreshed.                              
    token_expired(agavedb, token_endpoint)

    agave_context = get_agave_context(agavedb)

    access_token = agave_context["current"].get("access_token", "")
    if access_token == "":
        print("No access token. Create one (you may need to create a client as well)",
            file=sys.stderr)
        sys.exit(1)

    return access_token



def token_expired(agavedb, token_refresh_endpoint):
    """ Check if access token is expired

    Check if access token for Agave has expired
    """
    # Get baseurl for tenant.                                                   
    agave_context = get_agave_context(agavedb)

    created_t = int(agave_context["current"].get("created_at", 0))
    expires_t = int(agave_context["current"].get("expires_in", 0))
    expiration_t = created_t + expires_t
    if expiration_t == 0:
        print("It looks like you may not have an access token. Try \"auth create\"", 
                file=sys.stderr)
        sys.exit(1)

    delta_t = int(time.time()) - expiration_t
    if delta_t > -60:
        print("Refreshing token...")
        refresh_token(agavedb, token_refresh_endpoint)



def refresh_token(agavedb, endpoint):
    """ Retrieve a new Oauth bearer token

    PARAMETERS
    ----------
    agavedb : str
        Path to the directory where to save the agave db (agave.json).
    endpoint : str
        Endpoint to make request to (do not include '/' at begining).
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)
    
    # Make request.
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": agave_context["current"]["refresh_token"],
            "scope": "PRODUCTION"
        }

        key = agave_context["current"].get("apikey", None)
        secret = agave_context["current"].get("apisecret", None)
        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.post(endpoint, headers=headers, data=data, auth=(key, secret))
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    handle_bad_response_status_code(resp)

    # Update agave database.
    now = int(time.time())
    expires_at = now + int(resp.json()["expires_in"])
    agave_context["current"]["access_token"] = resp.json()["access_token"]
    agave_context["current"]["refresh_token"] = resp.json()["refresh_token"]
    agave_context["current"]["expires_in"] = resp.json()["expires_in"]
    agave_context["current"]["created_at"] = now
    agave_context["current"]["expires_at"] = time.strftime("%a %b %-d %H:%M:%S %Z %Y", time.localtime(expires_at))

    # Save data to Agave database.
    with open("{}/agave.json".format(agavedb), "w") as f:
        json.dump(agave_context, f, sort_keys=True, indent=4)
