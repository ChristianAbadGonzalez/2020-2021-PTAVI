#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}

    def expiration_time(self):
        e_usuarios = []
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        for user in self.dicc:
            exp = self.dicc[user]["expires"]
            if now >= exp:
                e_usuarios.append(user)
        for user in e_usuarios:
            del self.dicc[user]

    def register2json(self):
        with open("registered.json", "w") as jsonfile:
            json.dump(self.dicc, jsonfile, indent=3)

    def json2register(self):
        try:
            with open("registered.json", "r") as jsonfile:
                self.dicc = json.load(jsonfile)
        except:
            pass

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        self.json2register()
        ip = self.client_address[0]
        port = self.client_address[1]
        data = self.rfile.read().decode("utf-8")
        usuario = data.split()[1].split(":")[1]
        expires = data.split("\r\n")[1].split()[1]
        if int(expires) != 0:
            exp = time.gmtime(time.time() + int(expires))
            xtime = time.strftime("%Y-%m-%d %H:%M:%S", exp)
            self.dicc[usuario] = {"address": ip, "expires": xtime}
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        else:
            if usuario in self.dicc:
                del self.dicc[usuario]
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        print(data)
        self.expiration_time()
        self.register2json()


if __name__ == "__main__":
    # Listens at localhost ('') port 6001
    # and calls the EchoHandler class to manage the request
    if len(sys.argv) != 2:
        sys.exit("Usage Error: python3 server.py port")
    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit("Port must be a number")
    serv = socketserver.UDPServer(('', port), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
