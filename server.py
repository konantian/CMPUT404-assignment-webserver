#  coding: utf-8
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Yuan Wang
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import os, os.path


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        if self.data:
            payload = self.data.decode().split()
            method, request_path = payload[0], payload[1]

            if method == "GET":
                if self.validPath(request_path):
                    if request_path.endswith("html") or request_path.endswith("css"):
                        file_path = "./www{}".format(request_path)
                        if os.path.isfile(file_path):
                            content = open(file_path, "r").read()
                            content_type = (
                                "text/html"
                                if request_path.endswith("html")
                                else "text/css"
                            )
                            header = self.createNormalHeader(
                                "HTTP/1.1 200 OK", content_type, content
                            ).encode()
                            self.request.sendall(header)
                        else:
                            self.send4XXHeader("404")

                    elif request_path.endswith("/"):
                        file_path = "./www{}index.html".format(request_path)
                        if os.path.isfile(file_path):
                            index_page = open(file_path, "r").read()
                            header = self.createNormalHeader(
                                "HTTP/1.1 200 OK", "text/html", index_page
                            ).encode()
                            self.request.sendall(header)
                        else:
                            self.send4XXHeader("404")

                    else:
                        if os.path.isfile("./www{}/index.html".format(request_path)):
                            status_code = "HTTP/1.1 301 Moved Permanently"
                            location = "Location: http://127.0.0.1:8080{}/".format(
                                request_path
                            )
                            header = "{0}\r\n{1}\r\n{2}".format(
                                status_code, location, "\r\n"
                            ).encode()
                            self.request.sendall(header)
                        else:
                            self.send4XXHeader("404")
                else:
                    self.send4XXHeader("404")
            else:
                self.send4XXHeader("405")

    def send4XXHeader(self, code):
        if code == "404":
            content = "<!DOCTYPE html><html><body><h1>404 Not Found</h1><p>The requsted resource cannot be accessed.</p></body></html>"
        else:
            content = "<!DOCTYPE html><html><body><h1>405 Method Not Allowed</h1><p>The request method is not allowed</p></body></html>"
        status_code = (
            "HTTP/1.0 404 Not Found"
            if code == "404"
            else "HTTP/1.0 405 Method Not Allowed"
        )
        header = self.createNormalHeader(status_code, "text/html", content).encode()
        self.request.sendall(header)

    def createNormalHeader(self, status_code, content_type, content):

        content_type = "Content-Type: {}".format(content_type)
        content_length = "Content-Length: {}".format(len(content))
        empty_header = "\r\n"

        return "{0}\r\n{1}\r\n{2}\r\n{3}{4}".format(
            status_code, content_type, content_length, empty_header, content
        )

    def validPath(self, path):

        current_path = os.getcwd()
        real_path = os.path.realpath("{}/www{}".format(current_path, path))

        return (
            os.path.exists(real_path)
            and os.path.commonpath([current_path, real_path]) == current_path
        )


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
