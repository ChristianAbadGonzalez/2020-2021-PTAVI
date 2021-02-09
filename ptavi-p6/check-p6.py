#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script de comprobación de entrega de práctica

Para ejecutarlo, desde la shell:
 $ python3 check-p6.py login_laboratorio

"""

import os
import random
import sys


files = ['README.md',
         'LICENSE',
         '.gitignore',
         '.gitlab-ci.yml',
         'client.py',
         'server.py',
         'simplertp.py',
         'bitstring.py',
         'invite.libpcap',
         'check-p6.py',
         '.git',
         'cancion.mp3']


if len(sys.argv) != 2:
    print()
    sys.exit("Usage: $ python3 check-p6.py --local | login_gitlab")

if sys.argv[1] == '--local':
    repo_git = "."
else:
    repo_git = "http://gitlab.etsit.urjc.es/" + sys.argv[1] + "/ptavi-p6"

aleatorio = str(int(random.random() * 1000000))

error = 0

print
if sys.argv[1] != '--local':
    print("Clonando el repositorio " + repo_git)
    print()
    os.system('git clone ' + repo_git + ' /tmp/' + aleatorio + ' > /dev/null 2>&1')
    try:
        student_file_list = os.listdir('/tmp/' + aleatorio)
    except OSError:
        error = 1
        sys.exit("Error: No se ha podido acceder al repositorio correctamente: " + repo_git)
else:
    student_file_list = os.listdir('.')
    
if len(student_file_list) != len(files):
    error = 1
    print("Error: solamente hay que subir al repositorio los ficheros indicados en las guion de practicas, que son en total " + str(len(files)) + " (incluyendo .git y .gitignore).")
    print("Has entregado " + str(len(student_file_list)) + " ficheros")

if set(files) != set(student_file_list):
    error = 1
    print()
    print("Algunos ficheros no se han entregado (o llamado) correctamente")
    demenos = set(files) - set(student_file_list)
    if demenos:
        print("Fichero(s) que falta(n) por entregar:", demenos)
    demas = set(student_file_list) - set(files)
    if demas:
        print("Fichero(s) entregado(s) de más:", demas)
    print()

if error:
    sys.exit("Ojo, hubo errores")
else:
    print("Parece que la comprobación de la entrega se ha realizado bien.")
    print("Recuerda que también tienes que pasar pycodestyle.")
    print()
