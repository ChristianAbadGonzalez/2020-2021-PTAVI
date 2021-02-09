#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente UDP que abre un socket a un servidor
"""

import socket
import sys


if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit("Usage Error: python3 client.py ip puerto register usuario expires")
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        usuario = sys.argv[4]
        expires = int(sys.argv[5])
        # " ".join --> es la función inversa del split
    except ValueError:
        sys.exit("Port must be a number")

    # Creamos el socket,
    # lo configuramos y lo atamos a un servidor/puerto.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((ip, port))
        line = "REGISTER sip:# SIP/2.0\r\n".replace("#", usuario)
        header = "Expires: #\r\n\r\n".replace("#", str(expires))
        line += header
        print("Enviando:", line)
        my_socket.send(bytes(line, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)
        print('Recibido -- ', data.decode('utf-8'))

    print("Socket terminado.")
