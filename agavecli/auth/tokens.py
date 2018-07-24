"""
    tokens.py
"""
from __future__ import print_function
import getpass
import json
import requests
import sys
import time
from os import path
from ..utils import get_access_token, get_agave_context, handle_bad_response_status_code



def token_create(agavedb, endpoint):
    """ Create Oauth bearer token
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)
    
    # Make request.
    try:
        data = {
            "username": agave_context["current"]["username"],
            "password": getpass.getpass(prompt="API password: "),
            "grant_type": "password",
            "scope": "PRODUCTION"
        }
        key      = agave_context["current"]["apikey"]
        secret   = agave_context["current"]["apisecret"] 
        params   = {"pretty": "true"}
        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.post(endpoint, data=data, params=params, auth=(key, secret))
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



def token_refresh(agavedb, endpoint):
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
        data = {
            "refresh_token": agave_context["current"]["refresh_token"],
            "grant_type": "refresh_token",
            "scope": "PRODUCTION"
        }
        key = agave_context["current"]["apikey"]
        secret = agave_context["current"]["apisecret"]
        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.post(endpoint, data=data, auth=(key, secret))
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
