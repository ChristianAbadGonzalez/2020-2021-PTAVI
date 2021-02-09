#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys


class Calculadora:

    def __init__(self, value1, value2):
        self.number1 = value1
        self.number2 = value2

    def plus(self):
        return self.number1 + self.number2

    def sub(self):
        return self.number1 - self.number2


if __name__ == "__main__":
    number1 = int(sys.argv[1])
    operation = sys.argv[2]
    number2 = int(sys.argv[3])
    cuenta = Calculadora(number1, number2)
    if operation == 'suma':
        print(cuenta.plus())
    elif operation == 'resta':
        print(cuenta.sub())
