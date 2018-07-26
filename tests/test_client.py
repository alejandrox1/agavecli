"""
    test_client.py
    
    Test "agavecli client" actions.
Client actions manage agave oauth clients. The local database can be located 
in ~/agave.json by default but other paths can be specify, make sure to keep 
track of this. See "agavecli tenant -h" for more information.
"""
import pytest
import json
import shutil
import tempfile
import agavecli
from agavecli_testsuite import MockServer
from http.server import BaseHTTPRequestHandler
from unittest.mock import patch

# Instace of local agave database used for testing the cli against agave api
# endpoints. Notice that the "baseurl" field points to "localhost."
sample_agavedb = {
    "current": {
        "access_token": "",
        "apikey": "",
        "apisecret": "",
        "baseurl": "http://localhost:{port}/",
        "created_at": "",
        "devurl": "",
        "expires_at": "",
        "expires_in": "",
        "refresh_token": "",
        "tenantid": "mocked tenant",
        "username": ""
    },
    "tenants": {}
}

# The agave API will provide a response with the following format upon a
# successfull attempt at creating a client.
sample_client_create_response = {
    "result": {
        "consumerKey": "this is a key",
        "consumerSecret": "this is a secret"
    }
}

# The agave API will provide a response with the following format upon a
# successfull attemp to delete a client.
sample_client_remove_response = {
    "status": "success",
    "message": "Client removed successfully.",
    "version": "2.0.0-SNAPSHOT-rc3fad",
    "result": {}
}

# The agave API will provide a response with the following format upon a
# successfull attempt to delete a client.
sample_client_list_response = {
    "status": "success",
    "message": "Clients retrieved successfully.",
    "version": "2.0.0-SNAPSHOT-rc3fad",
    "result": [{
        "description": None,
        "name": "DefaultApplication",
        "consumerKey": "Wxsaxaxsa",
        "_links": {
            "subscriber": {
                "href": "https://url/profiles/v2/user"
            },
            "self": {
                "href": "https://url/clients/v2/DefaultApplication"
            },
            "subscriptions": {
                "href":
                "https://url/clients/v2/DefaultApplication/subscriptions/"
            }
        },
        "tier": "Unlimited",
        "callbackUrl": None
    }]
}


class MockServerClientEndpoints(BaseHTTPRequestHandler):
    """ Mock the Agave API

    Mock client managament endpoints from the agave api.
    """

    def do_POST(self):
        """ Test agave client creation

        Mock endpoint for "agavecli client create" command.
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_client_create_response).encode())

    def do_DELETE(self):
        """ Test agave client removal

        Mock endpoint for "agavecli client rm" command.
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_client_remove_response).encode())

    def do_GET(self):
        """ Test agave client listing

        Mock endpoint for "agavecli client ls" command.
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_client_list_response).encode())


class TestMockServer(MockServer):
    """ Test client-related agave api endpoints 

    Tests client creation (HTTP POST request), removal (HTTP DELETE request), 
    and listing (HTTP GET request).
    """

    @classmethod
    def setup_class(cls):
        """ Set up an agave mock server

        Listen and serve mock api as a daemon.
        """
        MockServer.serve.__func__(cls, MockServerClientEndpoints)

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

    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_create(self, mock_input, mock_pass):
        """ Test "agavecli client create <client>"

        Patch username and password from user to send a client create request 
        to mock server.
        """
        # Patch username and password.
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()

            # cmd: agavecli client create -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(
                    ["client", "create", "-A", path])
            agavecli.main(args)
        finally:
            # Read and delete tmp instace f agave database.
            with open(path + "/agave.json", "r") as f:
                agavedb = json.load(f)
                shutil.rmtree(path)

        assert agavedb["current"]["apikey"] == \
                sample_client_create_response["result"]["consumerKey"]
        assert agavedb["current"]["apisecret"] == \
                sample_client_create_response["result"]["consumerSecret"]


    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_rm(self, mock_input, mock_pass, capfd):
        """ Test "agavecli client rm <client>

        Patch username and password from user to send a client delete request
        to mock server.
        """
        # Patch username and password.
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()

            # cmd: agavecli client create -n test_client -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(
                    ["client", "create", "-n", "test_client", "-A", path])
            agavecli.main(args)
            # cmd: agavecli client rm test_client -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(
                    ["client", "rm", "test_client", "-A", path])
            agavecli.main(args)
        finally:
            # Read and delete tmp instace f agave database.
            with open(path + "/agave.json", "r") as f:
                agavedb = json.load(f)
                shutil.rmtree(path)
        
        out, err = capfd.readouterr()
        assert out == ""
        assert "POST /clients/v2 HTTP/1.1\" 200" in err
        assert "DELETE /clients/v2/test_client HTTP/1.1\" 200" in err


    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_ls(self, mock_input, mock_pass, capfd):
        """ Test "agavecli client ls"

        Patch username and password from user to send a client list request   
        to mock server.
        """
        # Patch username and password.
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()

            # cmd: agavecli client ls -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(["client", "ls", "-A", path])
            agavecli.main(args)
        finally:
            # Read and delete tmp instace f agave database.
            with open(path + "/agave.json", "r") as f:
                agavedb = json.load(f)
                shutil.rmtree(path)

        out, err = capfd.readouterr()
        assert sample_client_list_response["result"][0]["name"] in out
        assert "GET /clients/v2 HTTP/1.1\" 200" in err
