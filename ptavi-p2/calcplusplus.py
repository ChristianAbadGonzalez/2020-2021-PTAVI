#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoohija
import csv

with open(sys.argv[1]) as csvfile:
    operaciones = csv.reader(csvfile)
    for operacion in operaciones:
        print(operacion)
        try:
            operador = operacion[0]
            result = float(operacion[1])

            for number in operacion[2:]:
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
                    print(operation + ' is not allowed')

        except ValueError:
            sys.exit('Not an integer number')
