#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Programa de cliente UDP que abre un socket a un servidor."""

import socket
import sys
import time
import hashlib
import secrets
import random
import simplertp
import numpy as np
import os

from uaserver import XMLReader, LogWriter
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

USAGE_ERROR = "Usage Error: python3 uaclient.py config method option [message]"
METHODS_ALLOWED = ["register", "invite", "bye", "message", "subscribe"]


def get_response(nonce, password, username):
    """Funcion para obtener el digest response."""
    m = hashlib.sha512()
    m.update(bytes(nonce, "utf-8"))
    m.update(bytes(username, "utf-8"))
    m.update(bytes(password, "utf-8"))
    return m.hexdigest()


class Methods():
    """Clase para devolver los mensajes SIP."""

    def __init__(self, src, ip_src, port_src, rtp_port, session_name="ssn"):
        """Funcion inicializadora."""
        self.src = src
        self.ip = ip_src
        self.port = port_src
        self.rtp = rtp_port
        self.ssn = session_name

    def register(self, option, response=""):
        """Funcion que devuelve los mensajes register."""
        line = "REGISTER sip:" + self.src + ":" + str(self.port)
        line += " SIP/2.0\r\nExpires: " + str(option)

        if response != "":

            line += "\r\nAuthorization: Digest response=\"" + response + "\""

        return line

    def invite(self, dst):
        """Funcion que devuelve los mensajes invite."""
        return "INVITE sip:" + dst + " SIP/2.0\r\n" + self.sdp()

    def ack(self, dst):
        """Funcion que devuelve los mensajes ack."""
        return "ACK sip:" + dst + " SIP/2.0"

    def bye(self, dst):
        """Funcion que devuelve los mensajes bye."""
        return "BYE sip:" + dst + " SIP/2.0"

    def message(self, dst, sms):
        """Funcion que devuelve los mensajes message."""
        line = "MESSAGE sip:" + dst + " SIP/2.0\r\nContent-Type: text/plain"
        line += "\r\nContent-Length: " + str(len(sms)) + "\r\n\r\n"
        return line + sms

    def subscribe(self):
        """Funcion que devuelve los mensajes subscribe."""
        return "SUBSCRIBE sip:" + self.src + " SIP/2.0"

    def sdp(self):
        """Funcion que devuelve el cuerpo SDP de un mensaje SIP."""
        line = "Content-Type: application/sdp\r\nContent-Length: "
        header = "v=0\r\no=" + self.src
        header += " " + self.ip + "\r\n"
        header += "s=" + self.ssn + "\r\nt=0\r\nm=audio " + str(self.rtp)
        header += " RTP"
        return line + str(len(header)) + "\r\n\r\n" + header


def correct_values(method):
    """Funcion para comprobar los datos introducidor por terminal."""
    if method in METHODS_ALLOWED:

        if method in ["register", "invite", "bye"]:

            if len(sys.argv) != 4:
                return False

            else:
                return True

        elif method == "message":

            if len(sys.argv) > 4:
                return True

            else:
                return False

        elif method == "subscribe":

            if len(sys.argv) != 3:
                return False

            else:
                return True

    else:
        return False


if __name__ == "__main__":

    try:
        method = sys.argv[2].lower()

        if not correct_values(method):
            sys.exit(USAGE_ERROR)

        config = sys.argv[1]
        method = sys.argv[2]
        parser = make_parser()
        cHandler = XMLReader()
        parser.setContentHandler(cHandler)
        parser.parse(open(config))
        tags = cHandler.get_tags()
        ip = tags["regproxy"]["ip"]
        port = int(tags["regproxy"]["puerto"])
        log = LogWriter(tags["log"])
        log.starting()
        src = tags["account"]["username"]
        ip_src = tags["uaserver"]["ip"]
        port_src = int(tags["uaserver"]["puerto"])
        rtp_port = int(tags["rtpaudio"]["puerto"])
        message = Methods(src, ip_src, port_src, rtp_port, "mysession")

    except ValueError:
        log.error("Port must be a number")
        log.finishing()
        sys.exit("Port must be a number")

    except IndexError:
        sys.exit(USAGE_ERROR)

    if method.lower() == "register":
        option = sys.argv[3]
        mess = message.register(int(option))

    if method.lower() == "invite":
        option = sys.argv[3]
        mess = message.invite(option)

    if method.lower() == "bye":
        option = sys.argv[3]
        mess = message.bye(option)

    if method.lower() == "message":
        option = sys.argv[3]
        sms = " ".join(sys.argv[4:])

        mess = message.message(option, sms)

    if method.lower() == "subscribe":
        mess = message.subscribe()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((ip, port))
        my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
        log.sent_to(ip, port, mess)
        data = my_socket.recv(1024).decode('utf-8')
        log.received_from(ip, port, data)
        print('Recibido -- ', data)

        trying = "100 Trying"
        ringing = "180 Ringing"
        ok = "200 OK"

        if "401 Unauthorized" in data:
            nonce = data.split("\"")[1]
            password = tags["account"]["passwd"]
            response = get_response(nonce, src, password)
            mess = message.register(int(option), response)
            my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
            log.sent_to(ip, port, mess)
            data = my_socket.recv(1024).decode('utf-8')
            log.received_from(ip, port, data)
            print(data)

        elif trying in data and ringing in data and ok in data:
            mess = message.ack(option)
            my_socket.send(bytes(mess, "utf-8") + b"\r\n")
            log.sent_to(ip, port, mess)

            nb = 15

            BIT = int(secrets.choice(np.binary_repr(secrets.randbits(nb))))
            ALEAT = random.randint(0, nb)

            RTP_header = simplertp.RtpHeader()
            RTP_header.set_header(marker=BIT, cc=ALEAT)

            csrc = []

            for i in range(5):
                csrc.append(random.randint(0, 15))

            RTP_header.setCSRC(csrc)
            audio = simplertp.RtpPayloadMp3(tags["audio"])
            ip = data.split("\r\n")[10].split()[1]
            port = int(data.split("\r\n")[13].split()[1])
            simplertp.send_rtp_packet(RTP_header, audio, ip, port)
            os.system("cvlc rtp://@" + ip + ":" + str(port))

    print("Socket terminado.")
    log.finishing()
