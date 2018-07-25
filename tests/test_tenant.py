import pytest
import json
import requests
import shutil
import tempfile
import agavecli

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
    args = agavecli.main_parser.parse_args(["tenant", "ls"])
    agavecli.main(args)
    out, err = capfd.readouterr()
    assert "CODE                 NAME                                     URL" in out
    assert err == ""


def test_tenant_ls_Herr(capfd):
    with pytest.raises(SystemExit) as e:
        args = agavecli.main_parser.parse_args(["tenant", "ls", "-H", "http"])
        agavecli.main(args)
        out, err = capfd.readouterr()
        assert out == ""
        assert err == "Invalid URL 'http': No schema supplied. Perhaps you meant http://http?\n"
        assert e.type == SystemExit
        assert e.value.code == 1


def test_tenant_init():
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
