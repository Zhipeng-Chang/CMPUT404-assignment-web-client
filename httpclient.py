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

# Reference: https://docs.python.org/3/library/urllib.parse.html

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko)'


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsedUrl = urlparse(url)
        host = parsedUrl.hostname
        port = parsedUrl.port

        if host is None:
	    raise Exception("Could not resolve host.")

        if port is None:
            # Reference: https://eclass.srv.ualberta.ca/pluginfile.php/4549769/mod_resource/content/2/04-HTTP.pdf
            port = 80

        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.splitlines()[0].split(" ")[1]
        code = int(code)
        return code

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        headers = self.get_headers(data)
        body = data.replace(headers+"\r\n\r\n","")
        return body

    def get_path(self, url):
        path = url.replace(urlparse(url).scheme+"://"+urlparse(url).netloc,"")
        if len(path) == 0:
            path = "/"

        return path
    def get_args(self, args):
        var_arg=""
        if args is not None:
            var_arg = urlencode(args)

        return var_arg, len(var_arg)
    
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
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        self.connect(host, port)
        request_body = ('GET %s HTTP/1.1\r\nUser-Agent: %s\r\nHost: %s \r\nConnection: close\r\n\r\n'%(path, USER_AGENT, host))
        self.sendall(request_body)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        headers = self.get_headers(data)
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        self.connect(host, port)
        var_arg, contentLength = self.get_args(args)
        request_body = ('POST %s HTTP/1.1\r\nUser-Agent: %s\r\nHost: %s \r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length:%s\r\nConnection: close\r\n\r\n%s'%(path, USER_AGENT, host, contentLength,var_arg))
        self.sendall(request_body)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        headers = self.get_headers(data)
        print(body)
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
