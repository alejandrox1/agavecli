"""
    clients.py
"""
from __future__ import print_function
from builtins import input
import getpass
import json
import requests
import sys
from os import path
from ..utils import get_agave_context, handle_bad_response_status_code



def client_create(agavedb, endpoint, client_name, description):
    """ Create an Agave client

    Send a request to the Agave service and update the local Agave database
    with the returned key and secret.
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)
    
    # Make request.
    try:
        username = agave_context["current"].get("username", "")
        if username == "":
            username = input("API username: ")
        passwd = getpass.getpass(prompt="API password: ")

        data = {
            "clientName": client_name,
            "description": description,
            "tier": "Unlimited",
            "callbackUrl": "",
        }
        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.post(endpoint, data=data, auth=(username, passwd))
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    handle_bad_response_status_code(resp)

    # Update agave database with apikey(consumerKey) and apisecret(consumerSecret).
    agave_context["current"]["username"] = username
    agave_context["current"]["apikey"] = resp.json()["result"]["consumerKey"]
    agave_context["current"]["apisecret"] = resp.json()["result"]["consumerSecret"]
    agave_context["current"]["access_token"] = ""
    agave_context["current"]["refresh_token"] = ""
    agave_context["current"]["created_at"] = ""
    agave_context["current"]["expires_at"] = ""
    agave_context["current"]["expires_in"] = ""

    # Save data to Agave database.
    with open("{}/agave.json".format(agavedb), "w") as f:
        json.dump(agave_context, f, sort_keys=True, indent=4)



def client_delete(agavedb, endpoint, client_name):
    """ Delete an API client
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)

    # Make request.
    try:
        username = agave_context["current"].get("username", "")
        if username == "":
            username = input("API username: ")
        passwd = getpass.getpass(prompt="API password: ")
        
        endpoint = "{0}{1}/{2}".format(agave_context["current"]["baseurl"], endpoint, client_name)
        resp = requests.delete(endpoint, auth=(username, passwd))
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    handle_bad_response_status_code(resp)

    # Update agave database with apikey(consumerKey) and apisecret(consumerSecret).
    agave_context["current"]["apikey"] = ""
    agave_context["current"]["apisecret"] = ""

    # Save data to Agave database.
    with open("{}/agave.json".format(agavedb), "w") as f:
        json.dump(agave_context, f, sort_keys=True, indent=4)



def client_list(agavedb, endpoint):
    """ List API clients

    List all Agave API clients registered with the current tenant.
    """
    # Get baseurl for tenant.
    agave_context = get_agave_context(agavedb)

    # Make request.
    try:
        username = agave_context["current"].get("username", "")
        if username == "":
            username = input("API username: ")
        passwd = getpass.getpass(prompt="API password: ")

        endpoint = "{0}{1}".format(agave_context["current"]["baseurl"], endpoint)
        resp = requests.get(endpoint, auth=(username, passwd))
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    handle_bad_response_status_code(resp)

    # Print results.
    print("{0:<30} {1:<80}".format("NAME", "DESCRIPTION"))
    for client in resp.json()["result"]:
        description = client["description"] if client["description"] else ""
        print("{0:<30} {1:<80}".format(client["name"], description))
