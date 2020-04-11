#-----------------------------------------------------------------------------
#                           Author: fmash16
#-----------------------------------------------------------------------------

#!/usr/bin/env python

from __future__ import print_function

red = "\033[1;31m"
green = "\033[1;32m"
clr = "\033[0m"

import sys
import socket
import threading

# A thread class for handling multiple requests at the same time
class myThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn 

    def run(self):
        serve(self.conn)

# This function runs the main job of serving the required data and sending
# a proper response. This funciton assembles the other basic funcitons
def serve(conn):
    req_headers = handle_req(conn)
    status_code, data, content_type = get_data(req_headers)
    if status_code == 200:
        send_response_ok(conn, data, status_code, content_type)
    if status_code == 404:
        send_response_notfound(conn, status_code)
    conn.close()

# Recieves the client request, seperates the parameters supplied and returns
# them in a dictionary req_headers
def handle_req(conn):
    req = conn.recv(10000)
    params = req.split('\r\n') 
    req_headers = {}

    first = params[0].split(' ')
    req_headers['Method'] = first[0]
    req_headers['Path'] = first[1]
    req_headers['Ver'] = first[2]
    del params[0]
    del params[-2:]

    for lines in params:
         keys = lines.split(':', 1)
         req_headers[keys[0]] = keys[1].strip()

    return req_headers

# Gets data from the requested content files. Returns the data, the content
# type and the status code based on the availability of the file
def get_data(req_headers):
    if req_headers['Path'] == '/':
        req_headers['Path'] = '/index.html'
    obj = req_headers['Path'][1:]
    content_type = obj.split('.')[1]
    data = ""
    try:
        f = open(obj, 'r')
        status_code = 200
        for lines in f.readlines():
            data += lines
        f.close()
    except IOError:
        status_code = 404

    return [status_code, data, content_type]
                
# Sends the response to the client with the requested content with status code
# 200
def send_response_ok(conn, content_data, status_code, content_type):
    conn.send("HTTP/1.1 {}\r\n".format(status_code)
            + "Server: fmash server\r\n"
            + "Content-Length: {}\r\n".format(len(content_data))
            + "Content-type: {}\r\n".format(content_type)
            + "Connection: close\r\n\r\n")
    conn.send(content_data)

# Sends the error message on unavailability of the file
def send_response_notfound(conn, status_code):
    conn.send("HTTP/1.1 {}\r\n".format(status_code)
            + "Server: fmash server\r\n"
            + "Connection: close\r\n\r\n")
    conn.send("404 Not found")


# The main function asks for the port, creates a socket on localhost on that
# port and establishes a tcp connection with the client. On getting a new
# client, opens a new thread. The server is stopped only on keyboard interrupt.
if __name__ == "__main__":
    port = int(sys.argv[1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', port))
    print("{}[+]{} Server started on port {}.".format(green, clr, port))
    sock.listen(1)
    try:
        while True:
            conn, addr = sock.accept()
            print("{}[+] Incomming connection from {}{}".format(green,addr,clr))
            thread = myThread(conn)
            thread.start()
    except KeyboardInterrupt:
        print("\n{}[-]{} Server stopped.".format(red, clr))
