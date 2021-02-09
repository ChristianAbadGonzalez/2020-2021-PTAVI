#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Programa cliente que abre un socket a un servidor."""

import socket
import sys

usage_error = "Usage Error: python3 client.py method "
usage_error += "receptor@ipreceptor:portsip"

# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) == 3:
    method = sys.argv[1]
    user = sys.argv[2]
else:
    sys.exit(usage_error)

# Contenido que vamos a enviar
try:
    user_name = user.split("@")[0]
    server_ip = user.split("@")[1].split(":")[0]
    server_port = int(user.split("@")[1].split(":")[1])
except ValueError:
    sys.exit(usage_error)

# Creando contenido del mensaje
if method.lower() == "invite":
    LINE = "INVITE sip:" + user_name + "@" + server_ip + " SIP/2.0\r\n"
    ACK = "ACK sip:" + user_name + "@" + server_ip + " SIP/2.0\r\n"

if method.lower() == "bye":
    LINE = "BYE sip:" + user_name + "@" + server_ip + " SIP/2.0\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((server_ip, server_port))

    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024).decode("utf-8")

    print('Recibido -- ', data)
    if "100 Trying" in data and "180 Ringing" in data and "200 OK" in data:
        my_socket.send(bytes(ACK, "utf-8") + b"\r\n")

    print("Terminando socket...")

print("Fin.")
