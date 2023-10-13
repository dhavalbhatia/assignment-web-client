#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# ------------REFERENCES------------

# 1. query parameters from dict: 
#    https://stackoverflow.com/questions/40557606/how-to-url-encode-in-python-3
# 2. default content-type: 
#    https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
# 3. format http request:
#    https://docs.netscaler.com/en-us/citrix-adc/current-release/appexpert/http-callout/http-request-response-notes-format.html#format-of-an-http-request
#    lab 2 (proxy_client.py)
# 4. path in request:
#    https://www.ibm.com/docs/en/cics-ts/5.3?topic=protocol-http-requests

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(" ")
        code = code[1]
        return int(code)

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")
        if body[1]:
            body = body[1]
            return body
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        # handle args- need to be key=value pairs joined by &
        if args != None:
            query_parameter = urllib.parse.urlencode(args)
        else:
            query_parameter = ''
            
        parsed_url = urllib.parse.urlparse(url)

        # get path
        if parsed_url.path != '':
            path = parsed_url.path    
        else:
            path = '/'

        # formatting request to be sent
        http_request = (f"GET {path}?{query_parameter} HTTP/1.1\r\n"
                        f"Host: {parsed_url.hostname}\r\n"
                        f"Connection: close\r\n\r\n")

        # get port number connect to server
        if parsed_url.port:
            self.connect(parsed_url.hostname, parsed_url.port)
        else:
            self.connect(parsed_url.hostname, 80)
        
        self.sendall(http_request)
        
        # get response data, code and body
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        parsed_url = urllib.parse.urlparse(url)
        
        # get content
        if args != None:
            args = urllib.parse.urlencode(args)
        else:
            args = ''
        
        # get path
        if parsed_url.path != '':
            path = parsed_url.path    
        else:
            path = '/'
        
        http_request = (f"POST {path} HTTP/1.1\r\n"
                        f"Host: {parsed_url.hostname}\r\n"
                        f"Content-Length: {len(args)}\r\n"
                        f"Content-Type: application/x-www-form-urlencoded\r\n\r\n"
                        f"{args}")

        # get port and connect to server
        if parsed_url.port:
            self.connect(parsed_url.hostname, parsed_url.port)
        else:
            self.connect(parsed_url.hostname, 80)
        
        self.sendall(http_request)
        
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
