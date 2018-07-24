import pytest
import json
import shutil
import socket
import tempfile
import agavecli
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import patch

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

sample_post_response = {
    "result": {
        "consumerKey": "this is a key",
        "consumerSecret": "this is a secret"
    }
}

sample_get_response = {
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

sample_delete_response = {
    "status": "success",
    "message": "Client removed successfully.",
    "version": "2.0.0-SNAPSHOT-rc3fad",
    "result": {}
}


class MockServerRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_post_response).encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_get_response).encode())

    def do_DELETE(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_delete_response).encode())


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    addr, port = s.getsockname()
    s.close()
    return port


class TestMockServer:

    @classmethod
    def setup_class(cls):
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(("localhost", cls.mock_server_port),
                                     MockServerRequestHandler)

        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_create(self, mock_input, mock_pass):
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            sample_agavedb["current"]["baseurl"] = sample_agavedb["current"][
                "baseurl"].format(port=self.mock_server_port)
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

        args = agavecli.main_parser.parse_args(["client", "create", "-A", path])
        args.func(args)

        with open(path + "/agave.json", "r") as f:
            agavedb = json.load(f)
            shutil.rmtree(path)
        assert agavedb["current"]["apikey"] == sample_post_response["result"][
            "consumerKey"]
        assert agavedb["current"]["apisecret"] == sample_post_response[
            "result"]["consumerSecret"]


    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_rm(self, mock_input, mock_pass, capfd):
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            sample_agavedb["current"]["baseurl"] = sample_agavedb["current"][
                    "baseurl"].format(port=self.mock_server_port)
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

        args = agavecli.main_parser.parse_args(["client", "create", "-n", "test_client", "-A", path])
        args.func(args)
        args = agavecli.main_parser.parse_args(["client", "rm", "test_client", "-A", path])
        args.func(args)
        out, err = capfd.readouterr()
        with open(path + "/agave.json", "r") as f:
            agavedb = json.load(f)
            shutil.rmtree(path)
        
        assert out == ""
        assert "POST /clients/v2 HTTP/1.1\" 200" in err
        assert "DELETE /clients/v2/test_client HTTP/1.1\" 200" in err



    @patch("agavecli.clients.clients.input")
    @patch("agavecli.clients.clients.getpass.getpass")
    def test_client_ls(self, mock_input, mock_pass, capfd):
        mock_input.return_value = "hi"
        mock_pass.return_value = "pass"

        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            sample_agavedb["current"]["baseurl"] = sample_agavedb["current"][
                "baseurl"].format(port=self.mock_server_port)
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

        args = agavecli.main_parser.parse_args(["client", "ls", "-A", path])
        args.func(args)
        out, err = capfd.readouterr()

        with open(path + "/agave.json", "r") as f:
            agavedb = json.load(f)
            shutil.rmtree(path)
        assert sample_get_response["result"][0]["name"] in out
        assert "GET /clients/v2 HTTP/1.1\" 200" in err
