#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoohija


fich = open(sys.argv[1], 'r')
operaciones = fich.read()

for operacion in operaciones.split('\n'):
    if operacion != (""):
        print(operacion)
        try:
            operador = operacion.split(',')[0]
            result = float(operacion.split(',')[1])

            for number in operacion.split(',')[2:]:
                Not_Allowed = False
                operando = float(number)
                cuenta = calcoohija.CalculadoraHija(result, operando)

                if operador == 'suma':
                    result = cuenta.plus()

                elif operador == 'resta':
                    result = cuenta.sub()

                elif operador == 'multiplica':
                    result = cuenta.mux()

                elif operador == 'divide':
                    result = cuenta.div()

                else:
                    Not_Allowed = True

                if not Not_Allowed:
                    print(result)
                else:
                    print(operador + ' is not allowed')

        except ValueError:
            sys.exit('Not an integer number')
fich.close()
