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

# python3 httpclient.py GET http://www.cs.ualberta.ca/

# python3 httpclient.py POST http://EFWEFWE/49872398432

# python3 httpclient.py GET http://slashdot.org

# Reference: https://docs.python.org/3/library/urllib.parse.html

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsedUrl = urlparse(url)
        host = parsedUrl.hostname
        port = parsedUrl.port
        path_and_more = url.replace(parsedUrl.scheme+"://"+parsedUrl.netloc,"")

        if port is None:
            port = 80

        if len(path_and_more) == 0:
            path_and_more = "/"

        return host, port, path_and_more

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.splitlines()[0].split(" ")[1]
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
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
        host, port, path_and_more = self.get_host_port(url)
        try:
            self.connect(host, port)
            request_body = ('GET %s HTTP/1.1\r\nHost: %s \r\n\r\n'%(path_and_more, host))
            self.sendall(request_body)
            meg = self.recvall(self.socket)
            code = self.get_code(meg)
            body = self.get_body(meg)
            print(meg)
            return HTTPResponse(code, body)

        except Exception as e:
            return HTTPResponse(404)


    def POST(self, url, args=None):
        var_arg=""
        host, port, path_and_more = self.get_host_port(url)
        try:
            self.connect(host, port)
            if args is not None:
                var_arg = urlencode(args)
            request_body = ('POST %s HTTP/1.1\r\nHost: %s \r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length:%s\r\n\r\n%s'%(path_and_more, host, str(len(var_arg)),var_arg))
            self.sendall(request_body)
            meg = self.recvall(self.socket)
            code = self.get_code(meg)
            body = self.get_body(meg)
            print(meg)
            return HTTPResponse(code, body)

        except Exception as e:
            return HTTPResponse(404)

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
