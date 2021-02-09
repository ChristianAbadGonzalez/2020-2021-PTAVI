#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase (y programa principal) para un servidor de eco en UDP simple."""


import socketserver
import sys
import os
import simplertp
import secrets
import numpy as np


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):
        """Funcion manejadora."""
        # Escribe dirección y puerto del cliente (de tupla client_address)
        message = self.rfile.read().decode("utf-8")
        method = message.split()[0]
        print(method, "Received")
        if method == "INVITE":
            try:
                header = message.split("\r\n")[0]
                sdp_body = message.split("\r\n")[1:]
                user_name = header.split()[1].split(":")[1].split("@")[0]
                ip = header.split()[1].split(":")[1].split("@")[1]
                sdp = "Content-Type: application/sdp\r\n\r\nv=0\r\n"
                sdp += "o=" + user_name + " " + ip + "\r\n"
                sdp += "s=my_session\r\nt=0\r\nm=audio 23032 RTP\r\n"
                m = "SIP/2.0 100 Trying\r\nSIP/2.0 180 Ringing\r\n"
                m += "SIP/2.0 200 OK\r\n"
                self.wfile.write(bytes(m+sdp, "utf-8") + b"\r\n")
            except IndexError:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n")
        elif method == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

        elif method == "ACK":
            # La importación del modulo secrets se utiliza para generar numeros
            # aleatorios criptograficamente fuertes
            # para administrar datos sensibles.
            # secrets.randbits nos da un número entero aleatorio
            # con el número de bits que le introducimos.
            # np.binary_repr realiza la función de
            # cambiar de base decimal a binario.
            # secrets.choice dado un string
            # nos devuelve un caracter aleatorio de ese string.
            BIT = int(secrets.choice(np.binary_repr(secrets.randbits(1704))))
            RTP_header = simplertp.RtpHeader()
            RTP_header.set_header(version=2, marker=BIT,
                                  payload_type=14, ssrc=200002)
            audio = simplertp.RtpPayloadMp3(fich)
            simplertp.send_rtp_packet(RTP_header, audio, "127.0.0.1", 23032)

        else:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 4:
            sys.exit("Usage Error: python3 server.py ip port audio_file")

        ip = sys.argv[1]
        port = int(sys.argv[2])
        fich = sys.argv[3]
        if not os.path.exists(fich):
            sys.exit("Usage Error: python3 server.py ip port audio_file")
    except ValueError:
        sys.exit("Usage Error: python3 server.py ip port audio_file")

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip, port), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        sys.exit("Server Finish")
