import pytest
import json
import shutil
import socket
import tempfile
import time
import agavecli
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import patch

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

sample_post_response = {
    "scope": "default",
    "token_type": "bearer",
    "expires_in": 14400,
    "refresh_token": "token1",
    "access_token": "token2"
}

        
        
class MockAuthCreate(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(sample_post_response).encode())


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
                                     MockAuthCreate)

        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    @patch("agavecli.auth.tokens.getpass.getpass")
    def test_auth_create(self, mock_pass, capfd):
        mock_pass.return_value = "pass"

        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            sample_agavedb["current"]["baseurl"] = sample_agavedb["current"][
                "baseurl"].format(port=self.mock_server_port)
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

        args = agavecli.main_parser.parse_args(["auth", "create", "-A", path])
        agavecli.main(args)
        out, err = capfd.readouterr()

        with open(path + "/agave.json", "r") as f:
            agavedb = json.load(f)
            shutil.rmtree(path)

        calct = int(time.time()) + int(sample_post_response["expires_in"])
        calct = time.localtime(calct)
        agavet = time.strptime(agavedb["current"]["expires_at"], "%a %b %d %H:%M:%S %Z %Y")

        assert agavet.tm_year == calct.tm_year
        assert agavet.tm_mon == calct.tm_mon
        assert agavet.tm_mday == calct.tm_mday
        assert agavet.tm_hour == calct.tm_hour


    @patch("agavecli.auth.tokens.getpass.getpass")
    def test_auth_refresh(self, mock_pass, capfd):
        mock_pass.return_value = "pass"

        path = tempfile.mkdtemp()
        with open(path + "/agave.json", "w") as f:
            sample_agavedb["current"]["baseurl"] = sample_agavedb["current"][
                "baseurl"].format(port=self.mock_server_port)
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

        args = agavecli.main_parser.parse_args(["auth", "create", "-A", path])
        agavecli.main(args)
        args = agavecli.main_parser.parse_args(["auth", "refresh", "-A", path])
        agavecli.main(args)
        out, err = capfd.readouterr()

        with open(path + "/agave.json", "r") as f:
            agavedb = json.load(f)
            shutil.rmtree(path)

        calct = int(time.time()) + int(sample_post_response["expires_in"])
        calct = time.localtime(calct)
        agavet = time.strptime(agavedb["current"]["expires_at"], "%a %b %d %H:%M:%S %Z %Y")

        assert agavet.tm_year == calct.tm_year
        assert agavet.tm_mon == calct.tm_mon
        assert agavet.tm_mday == calct.tm_mday
        assert agavet.tm_hour == calct.tm_hour
