import pytest
import json
import shutil
import socket
import tempfile
import time
import agavecli
from agavecli_testsuite import MockServer
from http.server import BaseHTTPRequestHandler
from unittest.mock import patch

# Instace of local agave database used for testing the cli against agave api    
# endpoints. Notice that the "baseurl" field points to "localhost."
sample_agavedb = {
    "current": {
        "access_token": "",
        "apikey": "key",
        "apisecret": "secret",
        "baseurl": "http://localhost:{port}/token",
        "created_at": "",
        "devurl": "",
        "expires_at": "",
        "expires_in": "",
        "refresh_token": "",
        "tenantid": "mocked tenant",
        "username": "user"
    },
    "tenants": {}
}

# The agave API will provide a response with the following format upon a
# successfull attempt to create or refresh an access token.
saple_auth_token_response = {
    "scope": "default",
    "token_type": "bearer",
    "expires_in": 14400,
    "refresh_token": "token1",
    "access_token": "token2"
}


class MockServerAuthEndpoints(BaseHTTPRequestHandler):
    """ Mock the Agave API                                                      
                                                                                
    Mock authentication  managament endpoints from the agave api.
    """
    def do_POST(self):
        """ Test agave token creation

        Mock endpoint for "agavecli auth create|refresh"
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(saple_auth_token_response).encode())


class TestMockServer((MockServer)):
    """ Test access token-related agave api endpoints                                 
    
    Tests access token creation and refreshment (HTTP POST request).
    """ 
    
    @classmethod
    def setup_class(cls):
        """ Set up an agave mock server

        Listen and serve mock api as a daemon.
        """
        MockServer.serve.__func__(cls, MockServerAuthEndpoints)

    def set_tmp_agave_db(self):
        """ Set up a temporary instance of a local agave database

        Set up an instance of the local agave database that points the current
        tenant's baseurl to the address of the mock server on the local host
        and mock the entry of username and password from the user.
        """
        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            # Set baseurl of current tenant to localhost to test agave API
            # endpoint with the mock server.
            baseurl = sample_agavedb["current"]["baseurl"]
            baseurl = baseurl.format(port=self.mock_server_port)
            sample_agavedb["current"]["baseurl"] = baseurl

            # Save changes to database.
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)
        
        return path

    @patch("agavecli.auth.tokens.getpass.getpass")
    def test_auth_create(self, mock_pass):
        """ Test "agavecli auth create"

        Patch username and password from user to send an access token create
        request to mock server.
        """
        # Patch user password.
        mock_pass.return_value = "pass"

        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()

            # cmd: agavecli auth create -A /tmp/<dir>
            args = agavecli.main_parser.parse_args(
                    ["auth", "create", "-A", path])
            agavecli.main(args)
        finally:
            # Read and delete tmp instace f agave database.
            with open(path + "/agave.json", "r") as f:
                agavedb = json.load(f)
                shutil.rmtree(path)

        calct = int(time.time()) + int(saple_auth_token_response["expires_in"])
        calct = time.localtime(calct)
        agavet = time.strptime(agavedb["current"]["expires_at"], "%a %b %d %H:%M:%S %Z %Y")

        assert agavet.tm_year == calct.tm_year
        assert agavet.tm_mon == calct.tm_mon
        assert agavet.tm_mday == calct.tm_mday
        assert agavet.tm_hour == calct.tm_hour


    @patch("agavecli.auth.tokens.getpass.getpass")
    def test_auth_refresh(self, mock_pass):
        """ Test "agavecli auth refresh"                              
                                                                                
        Patch username and password from user to send an access token refresh
        request to mock server.                                                         
        """
        # Patch user password.
        mock_pass.return_value = "pass"

        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()

            # cmd: agavecli auth create -A /tmp/<dir>
            args = agavecli.main_parser.parse_args(
                    ["auth", "create", "-A", path])
            agavecli.main(args)
            # cmd: agavecli auth refresh -A /tmp/<dir>
            args = agavecli.main_parser.parse_args(
                    ["auth", "refresh", "-A", path])
            agavecli.main(args)
        finally:
            # Read and delete tmp instace f agave database.
            with open(path + "/agave.json", "r") as f:
                agavedb = json.load(f)
                shutil.rmtree(path)

        calct = int(time.time()) + int(saple_auth_token_response["expires_in"])
        calct = time.localtime(calct)
        agavet = time.strptime(agavedb["current"]["expires_at"], "%a %b %d %H:%M:%S %Z %Y")

        assert agavet.tm_year == calct.tm_year
        assert agavet.tm_mon == calct.tm_mon
        assert agavet.tm_mday == calct.tm_mday
        assert agavet.tm_hour == calct.tm_hour
