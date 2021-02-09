#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase (y programa principal) para un servidor proxy SIP."""

import socketserver
import sys
import json
import time
import secrets
import hashlib
import socket as skt

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def parse_ip(ip):
    """Funcion para comprobar la formación de la IP."""
    if len(ip.split(".")) != 4:

        return False

    for n in ip.split("."):

        try:
            if int(n) > 255 or int(n) < 0:
                return False

        except ValueError:
            return False

    return True


def get_digest(password, username):
    """Funcion para obtener el digest nonce."""
    m = hashlib.md5()
    m.update(bytes(username, "utf-8"))
    m.update(bytes(password, "utf-8"))
    return m.hexdigest()


def get_response(nonce, password, username):
    """Funcion para obtener el digest response."""
    m = hashlib.sha512()
    m.update(bytes(nonce, "utf-8"))
    m.update(bytes(username, "utf-8"))
    m.update(bytes(password, "utf-8"))
    return m.hexdigest()


class XMLReader(ContentHandler):
    """Funcion para parsear ficheros 'XML'."""

    def __init__(self):
        """Funcion para inicializar los objetos 'XML-READER'."""
        self.dicc = {}
        self.attr = {"server": ["name", "ip", "puerto"],
                     "database": ["path", "passwdpath"],
                     "log": ["path"]}

    def startElement(self, name, attrs):
        """Funcion para inicializar un elemento."""
        if name in self.attr:
            dicc = {}

            for atributo in self.attr[name]:
                dicc[atributo] = attrs.get(atributo, "")

            self.dicc[name] = dicc

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


class SIPProxy(socketserver.DatagramRequestHandler):
    """SIP Proxy server class."""

    dicc = {}
    pwd = {}
    sessions = []

    def register2json(self):
        """Funcion para recoger datos 'json'."""
        with open(tags["database"]["path"], "w") as jsonfile:
            json.dump(self.dicc, jsonfile, indent=3)

    def json2register(self):
        """Funcion para devolver/guardar datos 'json'."""
        try:

            with open(tags["database"]["path"], "r") as jsonfile:
                self.dicc = json.load(jsonfile)

        except FileNotFoundError:
            pass

    def json2password(self):
        """Funcion para recoger datos 'json'."""
        try:

            with open(tags["database"]["passwdpath"], "r") as jsonfile:
                self.pwd = json.load(jsonfile)

        except FileNotFoundError:
            pass

    def ua_expires(self):
        """Funcion para eliminar a los usuarios que hayan expirado."""
        aux = self.dicc.copy()
        now = time.time() + 3600

        for user in aux:
            exp = self.dicc[user][2]

            if now >= exp:

                del self.dicc[user]

    def add_header(self, data):
        """Funcion para añadir la cabecera del Proxy."""
        line = ""

        for l in data.split("\r\n"):

            if self.is_init(l):
                line += l
                line += "\r\nVia: SIP/2.0/UDP " + tags["server"]["ip"] + ":"
                line += tags["server"]["puerto"] + "\r\n"

            else:
                line += l + "\r\n"

        return line

    def is_init(self, l):
        """Funcion que devuelve TRUE si es el inicio del mensaje."""
        method = "INVITE" in l or "REGISTER" in l or "ACK" in l or "BYE" in l
        method = method or "MESSAGE" in l
        tryringok = "100 Trying" in l or "180 Ringing" in l or "200 OK" in l
        unf = "404 User Not Found" in l
        br = "400 Bad Request" in l
        mna = "405 Method Not Allowed" in l

        return method or tryringok or unf or br or mna

    def parse_sdp(self, data):
        """Funcion que comprueba si el SDP esta bien formado."""
        content = "Content-Type" in data and "Content-Length" in data
        body = "v=" in data and "o=" in data and "s=" in data
        body = body and "t=" in data and "m=" in data
        for l in data.split("\r\n"):

            if "o=" in l:

                ip = l.split()[1]

        if not parse_ip(ip):

            return False

        try:

            for l in data.split("\r\n"):

                if "m=" in l:

                    port = int(l.split()[1])

        except ValueError:
            return False

        return content and body

    def in_session(self, username):
        """Funcion que comprueba si el usuario tiene una sesion iniciada."""
        for session in self.sessions:

            if username in session:
                return True

        return False

    def delete_session(self, username):
        """Funcion para eliminar sesiones activas."""
        s = self.sessions.copy()
        for i, session in enumerate(s):

            if username in session:
                del self.sessions[i]

    def send_notify(self, user, text):
        """Funcion para enviar mensajes notify."""
        line = "NOTIFY sip:#user# SIP/2.0\r\nReason: SIP; cause=200; text=\""
        line += user + " " + text + "\"\r\n"

        for user in self.dicc:

            if not self.dicc[user][3]:
                continue

            ip_dst = self.dicc[user][1]
            port_dst = self.dicc[user][0]
            mess = line.replace("#user#", user)

            with skt.socket(skt.AF_INET, skt.SOCK_DGRAM) as sck:
                sck.connect((ip_dst, port_dst))
                sck.send(bytes(mess, 'utf-8') + b'\r\n')
                log.sent_to(ip_dst, port_dst, mess)
                data = sck.recv(1024).decode("utf-8")
                log.received_from(ip_dst, port_dst, data)
                print(data)

    def handle(self):
        """Funcion manejadora de todos los mensajes SIP."""
        self.json2register()
        self.ua_expires()
        ip = self.client_address[0]
        port = self.client_address[1]
        data = self.rfile.read().decode("utf-8")
        log.received_from(ip, port, data)
        print(data)
        method = data.split()[0]

        if method.lower() == "register":
            try:
                username = data.split()[1].split(":")[1]
                user_port = int(data.split()[1].split(":")[2])
                expires = int(data.split("\r\n")[1].split()[1])

                if expires != 0:

                    if username in self.dicc:
                        tm = time.time() + 3600 + expires
                        self.dicc[username][2] = tm
                        self.wfile.write(b"SIP/2.0 200 OK\r\n")
                        log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")

                    else:
                        self.json2password()

                        if "Digest response" in data:

                            nonce = get_digest(username, self.pwd[username])
                            response = data.split("\"")[1]
                            pwd = self.pwd[username]

                            if secrets.compare_digest(get_response(nonce,
                                                                   username,
                                                                   pwd),
                                                      response):

                                tm = time.time() + 3600 + expires
                                ip = self.client_address[0]
                                self.dicc[username] = [user_port,
                                                       ip,
                                                       tm,
                                                       False]

                                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                                log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")
                                self.send_notify(username, "just registered")

                            else:
                                br = b"SIP/2.0 400 Bad Request\r\n"
                                self.wfile.write(br)
                                log.sent_to(ip, port, br.decode("utf-8"))

                        else:
                            line = "SIP/2.0 401 Unauthorized\r\n"
                            nonce = get_digest(username, self.pwd[username])
                            line += "WWW Authenticate: Digest nonce=\""
                            line += nonce + "\"\r\n"
                            self.wfile.write(bytes(line, "utf-8"))
                            log.sent_to(ip, port, line)

                else:

                    if username in self.dicc:

                        del self.dicc[username]
                        self.send_notify(username, "leaves the chat")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n")
                        log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")

                    else:
                        self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                        log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

            except ValueError:
                br = b"SIP/2.0 400 Bad Request\r\n"
                self.wfile.write(br)
                log.sent_to(ip, port, br.decode("utf-8"))

        elif method.lower() == "invite":
            try:

                if not self.parse_sdp(data):
                    raise NameError

                user_dst = data.split()[1].split(":")[1]
                user_src = data.split("\r\n")[5].split("=")[1].split()[0]

                if user_dst in self.dicc and user_src in self.dicc:
                    if [user_src, user_dst] not in self.sessions:
                        if [user_dst, user_src] not in self.sessions:
                            self.sessions.append([user_dst, user_src])

                    ip_dst = self.dicc[user_dst][1]
                    port_dst = self.dicc[user_dst][0]

                    with skt.socket(skt.AF_INET, skt.SOCK_DGRAM) as sck:
                        sck.connect((ip_dst, port_dst))
                        mess = self.add_header(data)
                        sck.send(bytes(mess, 'utf-8'))
                        log.sent_to(ip_dst, port_dst, mess)
                        data = sck.recv(1024).decode("utf-8")
                        log.received_from(ip_dst, port_dst, data)

                        if self.parse_sdp(data):
                            mess = self.add_header(data)
                            self.wfile.write(bytes(mess, "utf-8"))
                            log.sent_to(ip, port, mess)

                        else:
                            br = b"SIP/2.0 400 Bad Request\r\n"
                            sck.send(br)
                            log.sent_to(ip, port, br.decode("utf-8"))

                else:
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                    log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

            except NameError:
                br = b"SIP/2.0 400 Bad Request\r\n"
                self.wfile.write(br)
                log.sent_to(ip, port, br.decode("utf-8"))

            except ConnectionRefusedError:
                log.error("connection refused")

        elif method.lower() == "ack":
            user_dst = data.split()[1].split(":")[1]

            if user_dst in self.dicc:
                ip_dst = self.dicc[user_dst][1]
                port_dst = self.dicc[user_dst][0]

                with skt.socket(skt.AF_INET, skt.SOCK_DGRAM) as sck:
                    sck.connect((ip_dst, port_dst))
                    mess = self.add_header(data)
                    sck.send(bytes(mess, 'utf-8'))
                    log.sent_to(ip_dst, port_dst, mess)

            else:
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

        elif method.lower() == "bye":
            user_dst = data.split()[1].split(":")[1]

            if user_dst in self.dicc and self.in_session(user_dst):
                self.delete_session(user_dst)
                ip_dst = self.dicc[user_dst][1]
                port_dst = self.dicc[user_dst][0]

                with skt.socket(skt.AF_INET, skt.SOCK_DGRAM) as sck:
                    sck.connect((ip_dst, port_dst))
                    mess = self.add_header(data)
                    sck.send(bytes(mess, 'utf-8') + b'\r\n')
                    log.sent_to(ip_dst, port_dst, mess)
                    data = sck.recv(1024)
                    log.received_from(ip_dst, port_dst, data.decode("utf-8"))
                    mess = self.add_header(data.decode("utf-8"))
                    self.wfile.write(bytes(mess, "utf-8") + b"\r\n")
                    log.sent_to(ip, port, mess)

            else:
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

        elif method.lower() == "message":
            if "text/plain" in data:
                user_dst = data.split("\r\n")[0].split()[1].split(":")[1]

                if user_dst in self.dicc:
                    ip_dst = self.dicc[user_dst][1]
                    port_dst = self.dicc[user_dst][0]

                    with skt.socket(skt.AF_INET, skt.SOCK_DGRAM) as sck:
                        sck.connect((ip_dst, port_dst))
                        mess = self.add_header(data)
                        sck.send(bytes(mess, 'utf-8') + b'\r\n')
                        log.sent_to(ip_dst, port_dst, mess)

                else:
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                    log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n")
                log.sent_to(ip, port, "SIP/2.0 400 Bad Request\r\n")

        elif method.lower() == "subscribe":
            user_src = data.split()[1].split(":")[1]

            if user_src in self.dicc:
                self.dicc[user_src][3] = True
                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                log.sent_to(ip, port, "SIP/2.0 200 OK\r\n")

            else:
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n")
                log.sent_to(ip, port, "SIP/2.0 404 User Not Found\r\n")

        else:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n")
            log.sent_to(ip, port, "SIP/2.0 405 Method Not Allowed\r\n")
        self.register2json()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Usage Error: python3 proxy_registrar.py config")

    try:
        config = sys.argv[1]
        parser = make_parser()
        cHandler = XMLReader()
        parser.setContentHandler(cHandler)
        parser.parse(open(config))
        tags = cHandler.get_tags()
        ip = tags["server"]["ip"]
        port = int(tags["server"]["puerto"])
        log = LogWriter(tags["log"]["path"])

        if not parse_ip(ip):
            log.error("Out of range IP")
            sys.exit("Out of range IP")

    except ValueError:
        log.error("Port must be a number")
        sys.exit("Port must be a number")
    log.starting()
    serv = socketserver.UDPServer((ip, port), SIPProxy)

    line = "Server " + tags["server"]["name"] + " listening at port "
    line += tags["server"]["puerto"] + "..."
    print(line)

    try:
        serv.serve_forever()

    except KeyboardInterrupt:
        print("Finalizado servidor")
        log.finishing()
