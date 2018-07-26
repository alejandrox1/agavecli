"""
    test_files.py
"""
import pytest
import cgi
import filecmp
import json
import mimetypes
import os
import shutil
import tempfile
import time
import agavecli
from agavecli_testsuite import MockServer
try: # python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ModuleNotFoundError: # python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer

# Instace of local agave database used for testing the cli against agave api    
# endpoints. Notice that the "baseurl" field points to "localhost."             
sample_agavedb = {                                                              
    "current": {                                                                
        "access_token": "",                                                     
        "apikey": "key",                                                        
        "apisecret": "secret",                                                  
        "baseurl": "http://localhost:{port}/",                             
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

sample_file_upload_response = {
  "status" : "success",
  "message" : None,
  "version" : "2.2.21-xxxxx",
  "result" : {
    "name" : "file.ext",
    "uuid" : "xxxxxxxxxxx-xxxxxxxx-xxxx-xxx",
    "owner" : "user",
    "internalUsername" : None,
    "lastModified" : "2018-07-27T15:02:07.236-05:00",
    "source" : "http://ip/file.ext",
    "path" : "dir/file.ext",
    "status" : "STAGING_QUEUED",
    "systemId" : "tacc-globalfs-user",
    "nativeFormat" : "raw",
    "_links" : {
      "self" : {
        "href" : "https://tenant/files/v2/media/system/tacc-globalfs-user/dir/file.ext"
      },
      "system" : {
        "href" : "https://tenant/systems/v2/tacc-globalfs-user"
      },
      "profile" : {
        "href" : "https://tenant/profiles/v2/user"
      },
      "history" : {
        "href" : "https://tenant/files/v2/history/system/tacc-globalfs-user/dir/file.ext"
      },
      "notification" : [ ]
    }
  }
}

# curl -# -k -H "Authorization: Bearer <access token>" -X POST -F "fileToUpload=@file.txt" http://localhost:8080/files/v2/media/system/tacc-globalfs-user/testdir | jq .
# curl --form fileToUpload=@file.txt http://localhost:8080/files/v2/media/system/tacc-globalfs-user/testdir | jq .
# curl --head --location http://localhost:8080/f/file.txt
# curl -L http://localhost:8080/f/file.txt -o copy.txt
class MockServerFilesEndpoints(BaseHTTPRequestHandler):
    def send_headers(self):
        """ Send the appropiate HTTP headers for a given response

        The server has two resources to manage (endpoints): "/f" for querying
        files and "/upload" for uploading files. This helper functions sends
        the response headers base on the request received.
        """
        # The path corresponds to the service being queried. For example,
        # querying "http://localhost:80/f/file.txt" will set the path as
        # "/f/file.txt". 
        npath = os.path.normpath(self.path)
        npath = npath[1:]
        path_elements = npath.split("/")

        # Check access token
        try: # Python 2
            valid_access_token = self.headers.getheader("Authorization")
        except AttributeError: # Python 3
            valid_access_token = self.headers.get("Authorization")

        if not valid_access_token:
            self.send_error(401, "Unauthorized")
            return None

        # Query a file (/f/filename).
        if path_elements[0] == "f":  # "/f" source manages files.
            flocal = path_elements[1] # File name.

            if not os.path.isfile(flocal) or not os.access(flocal, os.R_OK):
                self.send_error(404, "file not found")
                return None

            content, encoding = mimetypes.MimeTypes().guess_type(flocal)
            if content is None:
                content = "application/octet-stream"

            info = os.stat(flocal)

            self.send_response(200)
            self.send_header("Content-Type", content)
            self.send_header("Content-Encoding", encoding)
            self.send_header("Content-Length", info.st_size)
            self.end_headers()

        # Upload a file.
        elif "/files/v2/media/system" in self.path: 
            self.send_response(200)
            self.send_header("Content-Type", "text/json; character=utf-8")
            self.end_headers()

        # Request is neither querying a file (/f) nor uploading one ("/upload).
        else:
            self.send_error(404, "fuck")
            return None
    
        return path_elements


    def do_HEAD(self):
        self.send_headers()

    def do_GET(self):
        """ Query a file

        Query a file stored in the current working directory.
        """
        # elements is a list of path elements, i.e., ["a", "b"] ~ "/a/b".
        elements = self.send_headers()
        if elements is None or not "/files/v2/media/system" in self.path:
            return

        # Send contents of file to wfile object.
        filename = elements[-1]
        if "?pretty=true" in filename: filename = filename[:-len("?pretty=true")]
        with open(filename, "rb") as f:
            shutil.copyfileobj(f, self.wfile)


    def do_POST(self):
        """ Upload file

        Save uploaded file to current working directory and send a response.
        """
        # elements is a list of path elements, i.e., ["a", "b"] ~ "/a/b".
        elements = self.send_headers()
        if elements is None or not "/files/v2/media/system" in self.path:
            return
        
        # Submitted form data.
        form = cgi.FieldStorage(
            fp = self.rfile,
            headers = self.headers,
            environ = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers["Content-Type"]
            })

        # Save uploaded file.
        fname = form["fileToUpload"].filename
        with open(fname, "wb") as flocal:
            shutil.copyfileobj(form["fileToUpload"].file, flocal)
        
        # Send response.
        request_source = self.headers.get("HOST")
        file_path      = "/".join(elements[5:] + [fname])
        system_id      = elements[4]
        request_url    = "".join(["https://tenant", self.path, "/", fname])
        system_url     = "".join(["https://tenant", "/systems/v2/", system_id])
        history_url    = "".join(["https://tenant", "/files/v2/history/system/", system_id, "/", file_path])  
        sample_file_upload_response["result"]["name"] = fname
        sample_file_upload_response["result"]["source"] = request_source
        sample_file_upload_response["result"]["path"] = file_path
        sample_file_upload_response["result"]["systemId"] = system_id
        sample_file_upload_response["result"]["_links"]["self"]["href"] = request_url
        sample_file_upload_response["result"]["_links"]["system"]["href"] = system_url
        sample_file_upload_response["result"]["_links"]["history"]["href"] = history_url
        try: # python 2
            self.wfile.write(json.dumps(sample_file_upload_response))
        except TypeError:
            self.wfile.write(json.dumps(sample_file_upload_response).encode())



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
        MockServer.serve.__func__(cls, MockServerFilesEndpoints)

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

    def create_valid_access_token(self, path_to_agavedb):
        """ Create what looks like a valid access token

        Modify sample agave database template to make it look as if the access
        token is valid. Currently, agavecli will use the timestamps to check 
        whether an access token is valid.
        """
        now = int(time.time())
        expires_at = now + 14400
        sample_agavedb["current"]["access_token"] = "access_token"
        sample_agavedb["current"]["refresh_token"] = "refresh_token"    
        sample_agavedb["current"]["expires_in"] = 14400
        sample_agavedb["current"]["created_at"] = now
        sample_agavedb["current"]["expires_at"] = time.strftime("%a %b %-d %H:%M:%S %Z %Y", time.localtime(expires_at))
        
        # Save data to Agave database.
        with open("{}/agave.json".format(path_to_agavedb), "w") as f:
            json.dump(sample_agavedb, f, sort_keys=True, indent=4)

    def create_local_dummy_file(self):
        """ Create a dummy file for testing

        Create a dummy file to test file copying with the cli. Emulate a file
        on a local system.
        """
        _, file_path = tempfile.mkstemp()
        try:
            with open(file_path, "w") as tmp:
                tmp.write("this is a test file\n")
        except:
            os.remove(file_path)

        return file_path

    def create_remote_dummy_file(self):
        """ Create a dummy file for testing

        Create a dummy file to test file copying with the cli. Emulate a file
        on a remote agave system.
        """
        tmp_filename = "thisisatest.txt"
        with open(tmp_filename, "w") as tmp:
            tmp.write("this emulates a file on a remote system\n")
        return tmp_filename

    def test_fs_cp_local_to_remote(self):
        """ Test file copying from the local to a remote system

        Test "agavecli fs cp" when copying a file from the local system to
        a remote one.
        """
        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()
            self.create_valid_access_token(path)
            tmp_file = self.create_local_dummy_file()
            
            # cmd: agavecli fs cp <file> agave://tacc-globalfs-user/ -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(["fs", "cp", tmp_file, "agave://tacc-globalfs-user/", "-A", path])
            agavecli.main(args)
        finally:
            _, tmp_filename = os.path.split(tmp_file)
            assert filecmp.cmp(tmp_file, tmp_filename)
        
            # rm agavedb dir.
            shutil.rmtree(path)
            # rm dummy file.
            os.remove(tmp_file)
            # rm dummy file in current working directory.
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)

    def test_fs_cp_remote_to_local(self):
        """ Test file copying from a remote to the local system

        Test "agavecli fs cp" when copying a file from a remote agave system
        to a local system.
        """
        try:
            # Create an instance of the agave databse in /tmp.
            path = self.set_tmp_agave_db()
            self.create_valid_access_token(path)
            tmp_file = self.create_remote_dummy_file()
            local_file = "{}/testfile.txt".format(path)

            # cmd: agavecli fs cp agave://tacc-globalfs-user/ <file> -A /tmp/<dir>.
            args = agavecli.main_parser.parse_args(["fs", "cp", "agave://tacc-globalfs-user/"+tmp_file, local_file, "-A", path])
            agavecli.main(args)
        finally:
            assert filecmp.cmp(tmp_file, local_file)

            # rm agavedb dir.
            shutil.rmtree(path)
            # rm dummy file in current working directory.
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
