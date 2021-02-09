#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoo


class CalculadoraHija(calcoo.Calculadora):

    def mux(self):
        return self.number1 * self.number2

    def div(self):
        try:
            return self.number1 / self.number2
        except ZeroDivisionError:
            print("The division by the number 'zero(0) is not allowed")


if __name__ == '__main__':
    correct_usage = ('operand1 <suma|resta|multiplicacion|division> operando2')
    operation = sys.argv[2]
    try:
        number1 = int(sys.argv[1])
        number2 = int(sys.argv[3])
    except ValueError:
        sys.exit('Non numerical parametres')
    except IndexError:
        sys.exit('Usage error: python3 calcoohija number1 cuenta number2')

    cuenta = CalculadoraHija(number1, number2)
    if operation == 'suma':
        print(cuenta.plus())
    elif operation == 'resta':
        print(cuenta.sub())
    elif operation == 'multiplicacion':
        print(cuenta.mux())
    elif operation == 'division':
        print(cuenta.div())
    else:
        print(operation + ' is not allowed')
