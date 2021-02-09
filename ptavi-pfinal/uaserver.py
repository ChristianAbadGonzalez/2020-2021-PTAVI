#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase para un servidor de reproduccion de audio RTP."""

import socketserver
import sys
import json
import time
import simplertp
import secrets
import random
import numpy as np
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XMLReader(ContentHandler):
    """Funcion para parsear ficheros 'XML'."""

    def __init__(self):
        """Funcion para inicializar los objetos 'XML-READER'."""
        self.tag = ""
        self.dicc = {}
        self.attr = {"account": ["username", "passwd"],
                     "uaserver": ["ip", "puerto"],
                     "rtpaudio": ["puerto"],
                     "regproxy": ["ip", "puerto"],
                     "log": [""],
                     "audio": [""]}

    def startElement(self, name, attrs):
        """Funcion para inicializar un elemento."""
        self.tag = name
        if name in self.attr:
            dicc = {}

            for atributo in self.attr[name]:
                dicc[atributo] = attrs.get(atributo, "")

            self.dicc[name] = dicc

    def endElement(self, name):
        """Funcion para finalizar un elemento."""
        self.tag = ""

    def characters(self, content):
        """Funcion para leer el contenido de una etiqueta."""
        if self.tag == "log":
            self.dicc[self.tag] = content

        if self.tag == "audio":
            self.dicc[self.tag] = content

    def get_tags(self):
        """Funcion para devolver/conseguir las etiquetas."""
        return self.dicc


class LogWriter():
    """Clase para escribir los ficheros 'LOG'."""

    def __init__(self, filename):
        """Funcion para inicializar los objetos de clase 'LOG-WRITER'."""
        self.filename = filename

    def sent_to(self, ip, port, message):
        """Funcion para escribir en el fichero los mensaje enviados."""
        line = "Sent to " + ip + ":" + str(port) + ": " + message
        self.write(line)

    def received_from(self, ip, port, message):
        """Funcion para escribir en el fichero los mensajes recibidos."""
        line = "Received from " + ip + ":" + str(port) + ": " + message
        self.write(line)

    def error(self, message):
        """Funcion para escribir los errores obtenidos en los ficheros."""
        line = "Error: " + message
        self.write(line)

    def starting(self):
        """Funcion para escribir en los ficheros el inicio de procesos."""
        line = "Starting..."
        self.write(line)

    def finishing(self):
        """Funcion para escribir en los ficheros el final de procesos."""
        line = "Finishing."
        self.write(line)

    def write(self, line):
        """Funcion para escribir en los ficheros."""
        now = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time() + 3600))
        with open(self.filename, "a") as log_file:
            log_file.write(now + " " + line.replace("\r\n", " ") + "\n")


class SIPUAServer(socketserver.DatagramRequestHandler):
    """Clase de servidor de reproduccion de audio RTP."""

    rtp = []

    def handle(self):
        """Funcion manejadora de todos los mensajes SIP."""
        ip = self.client_address[0]
        port = self.client_address[1]
        data = self.rfile.read().decode("utf-8")
        log.received_from(ip, port, data)
        print(data)

        if "400 Bad Request" not in data:

            method = data.split()[0]

            if method == "INVITE":
                self.rtp.append(int(data.split("\r\n")[9].split()[1]))
                self.rtp.append(data.split("\r\n")[6].split()[1])
                ssn = data.split("\r\n")[7].split("=")[1]

                trying = b"SIP/2.0 100 Trying\r\n"
                self.wfile.write(trying)
                log.sent_to(ip, port, trying.decode("utf-8"))

                ringing = b"SIP/2.0 180 Ringing\r\n"
                self.wfile.write(ringing)
                log.sent_to(ip, port, ringing.decode("utf-8"))

                ok = "SIP/2.0 200 OK\r\n" + self.sdp(ssn)
                self.wfile.write(bytes(ok, "utf-8"))
                log.sent_to(ip, port, ok)

            elif method == "ACK":

                if self.rtp != []:

                    nb = 15
                    b = secrets.randbits(nb)
                    BIT = int(secrets.choice(np.binary_repr(b)))
                    ALEAT = random.randint(0, nb)

                    RTP_header = simplertp.RtpHeader()
                    RTP_header.set_header(marker=BIT, cc=ALEAT)

                    csrc = []

                    for i in range(5):
                        csrc.append(random.randint(0, 15))

                    RTP_header.setCSRC(csrc)
                    audio = simplertp.RtpPayloadMp3(tags["audio"])
                    ip = self.rtp[1]
                    port = self.rtp[0]
                    simplertp.send_rtp_packet(RTP_header, audio, ip, port)
                    os.system("cvlc rtp://@" + ip + ":" + str(port))

                else:
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n")
                    log.sent_to(ip, port, "SIP/2.0 400 Bad Request\r\n")

            elif method == "BYE":
                self.rtp = []
                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")

            elif method == "MESSAGE":
                sms = data.split("\r\n")[5]
                print("Message received:", sms)

            elif method == "NOTIFY":
                text = data.split("\"")[1]
                print("Notify received:", text)
                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")

            else:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n")
                log.sent_to(ip, port, "SIP/2.0 405 Method Not Allowed\r\n")

    def sdp(self, ssn):
        """Funcion para devolver el cuerpo SDP de un mensaje SIP."""
        port = tags["rtpaudio"]["puerto"]
        line = "Content-Type: application/sdp\r\nContent-Length: "
        header = "v=0\r\no=" + tags["account"]["username"]
        header += " " + tags["uaserver"]["ip"] + "\r\n"
        header += "s=" + ssn + "\r\nt=0\r\nm=audio " + port
        header += " RTP\r\n"
        return line + str(len(header)) + "\r\n\r\n" + header


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Usage Error: python3 uaserver.py config")

    try:
        config = sys.argv[1]
        parser = make_parser()
        cHandler = XMLReader()

        parser.setContentHandler(cHandler)
        parser.parse(open(config))

        tags = cHandler.get_tags()
        log = LogWriter(tags["log"])

        ip = tags["uaserver"]["ip"]
        port = int(tags["uaserver"]["puerto"])

    except ValueError:
        log.error("Port must be a number")
        sys.exit("Port must be a number")
    log.starting()
    serv = socketserver.UDPServer((ip, port), SIPUAServer)

    print("Lanzando servidor UDP de eco...")

    try:
        serv.serve_forever()

    except KeyboardInterrupt:
        print("Finalizado servidor")
        log.finishing()
