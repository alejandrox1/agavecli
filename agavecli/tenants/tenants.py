"""
    tenants.py
"""
from __future__ import print_function
import json
import requests
import sys
from os import path


def get_tenants(hosturl):
    """ Get Agave tenants

    Get all Agave tenants for a given Agave host.

    PARAMETERS
    ----------
    hosturl: string
        URL to send GET request to. This resource should list all Agave
        tenants.
    """
    # Make request.
    try:
        resp = requests.get(hosturl)
    except requests.exceptions.MissingSchema as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    # Handle bad status code.
    if resp.status_code >= 400:
        print(
            "Bad GET request to {0}, status code {1}".format(
                hosturl, resp.status_code),
            file=sys.stderr)
        sys.exit(1)

    return resp.json()



def tenant_init(hosturl, tenant_name, agavedb):
    """ Initiate an Agave Tenant

    Create or switch the current context to a specified Agave tenant.
    The current context along with all previous used are stored in a
    local database (arguments.agavedb).

    PARAMETERS
    ----------
    arguments: object (argparse.Namespace)
        tenant_name: pecify the name of the Agave tenant to work with.
        hosturl: url of Agave system.
    """
    # Get a json of all Agave tenants.
    tenants = get_tenants(hosturl)

    list_of_tenants = [x["code"] for x in tenants["result"]]

    # Check if the given tenant is part of the specified Agave system.
    if tenant_name not in list_of_tenants:
        print("{0} is not a tenant in {1}".format(tenant_name, hosturl),
            file=sys.stderr)
        sys.exit(1)

    # Organize metadata for tenant context.
    tenant_context = dict()
    tenant_index = list_of_tenants.index(tenant_name)
    tenant_info = tenants["result"][tenant_index]

    tenant_context = {
        "tenantid": tenant_info["code"],
        "baseurl": tenant_info["baseUrl"],
        "devurl": "",
        "apisecret": "",
        "apikey": "",
        "username": "",
        "access_token": "",
        "refresh_token": "",
        "created_at": "",
        "expires_in": "",
        "expires_at": ""
    }

    # Agave Database.
    agavedb = "{}/agave.json".format(agavedb)
    # Read in Agave database if it doesn't already exist, else create one.
    if path.isfile(agavedb):
        with open(agavedb, "r") as f:
            agave_context = json.load(f)
    else:
        agave_context = dict()

    # "tenant init" is run for the first time so we have to set "current" and
    # add it to "tenants".
    if "tenants" not in agave_context:
        # No existing tenants so we just add the default tenant_context.
        agave_context["current"] = tenant_context
        # Create an emoty dictionary for "tenants" key.
        agave_context["tenants"] = dict()

        # Save current tenant context.
        agave_context["tenants"][tenant_info["code"]] = agave_context["current"]
    # "tenants" already exist so we just have to put the current tenant_context
    # back in.
    else:
        # Save current tenant context.
        agave_context["tenants"][agave_context["current"]["tenantid"]] = agave_context["current"]

        # Get the tenant context if we already have it stored, else just set it
        # as the default tenant_context.
        agave_context["current"] = agave_context["tenants"].get(
            tenant_info["code"], tenant_context)

    # Save data to Agave database.
    with open(agavedb, "w") as f:
        json.dump(agave_context, f, sort_keys=True, indent=4)



def tenant_list(hosturl):
    """ List Agave tenants

    List all Agave tenants for a given Agave host. Information listed is the
    name and the code of the tenant.

    PARAMETERS
    ----------
    arguments: object (argparse.Namespace)
        This object may contain the following attributes:
        - hosturl: string representing a url (optional).
    """
    # Get a json of all AGave tenants.
    tenants = get_tenants(hosturl)

    # Print results.
    print("{0:<20} {1:<40} {2:<50}".format("CODE", "NAME", "URL"))
    for tenant in tenants["result"]:
        print("{0:<20} {1:<40} {2:<50}".format(tenant["code"], tenant["name"],
                                               tenant["baseUrl"]))
