"""
    test_tenant.py

    Test "agavecli tenant" actions.
Tenant actions manage communication between the user and the Agave API by
means of a local database. The local database can be located in ~/agave.json 
by default but other paths can be specify, make sure to keep track of this. 
See "agavecli tenant -h" for more information.
"""
import pytest
import json
import requests
import shutil
import tempfile
import agavecli


# This is what the local agave database should look like after initiating two
# agave tenants (irec and sd2e) and using the sd2e tenant for work.
sample_agavedb = {
    "current": {
        "access_token": "",
        "apikey": "",
        "apisecret": "",
        "baseurl": "https://api.sd2e.org/",
        "created_at": "",
        "devurl": "",
        "expires_at": "",
        "expires_in": "",
        "refresh_token": "",
        "tenantid": "sd2e",
        "username": ""
    },
    "tenants": {
        "irec": {
            "access_token": "",
            "apikey": "",
            "apisecret": "",
            "baseurl": "https://irec.tenants.prod.tacc.cloud/",
            "created_at": "",
            "devurl": "",
            "expires_at": "",
            "expires_in": "",
            "refresh_token": "",
            "tenantid": "irec",
            "username": ""
        },
        "sd2e": {
            "access_token": "",
            "apikey": "",
            "apisecret": "",
            "baseurl": "https://api.sd2e.org/",
            "created_at": "",
            "devurl": "",
            "expires_at": "",
            "expires_in": "",
            "refresh_token": "",
            "tenantid": "sd2e",
            "username": ""
        }
    }
}


def test_tenant_ls(capfd):
    """ Test "agavecli tenant ls" command

    This command is suppose to return a list of agave tenants.
    """
    # cmd: agavecli tenant ls
    args = agavecli.main_parser.parse_args(["tenant", "ls"])
    agavecli.main(args)
    out, err = capfd.readouterr()
    assert "CODE                 NAME                                     URL" in out
    assert err == ""


def test_tenant_ls_Herr(capfd):
    """ Failure test "agavecli tenant ls

    Test the cli fails gracefully when provided with a bad agave endpoint.
    """
    with pytest.raises(SystemExit) as e:
        # cmd: agavecli tenant ls -H http
        args = agavecli.main_parser.parse_args(["tenant", "ls", "-H", "http"])
        agavecli.main(args)
        out, err = capfd.readouterr()
        assert out == ""
        assert err == "Invalid URL 'http': No schema supplied. Perhaps you meant http://http?\n"
        assert e.type == SystemExit
        assert e.value.code == 1


def test_tenant_init():
    """ Test "agavecli tenant init <tenant>

    Test initialization of local agave database. The command "tenant init" 
    should switch the current tenant in use to whatever tenant is specified. 
    If a tenant other than the current is specified, the current context will
    be stored in the database.
    """
    path = tempfile.mkdtemp()
    args = agavecli.main_parser.parse_args(
        ["tenant", "init", "sd2e", "-A", path])
    agavecli.main(args)
    args = agavecli.main_parser.parse_args(
        ["tenant", "init", "irec", "-A", path])
    agavecli.main(args)
    args = agavecli.main_parser.parse_args(
        ["tenant", "init", "sd2e", "-A", path])
    agavecli.main(args)
    with open(path + "/agave.json", "r") as f:
        agavedb = json.load(f)
        shutil.rmtree(path)

    assert sample_agavedb == agavedb
