fich = open('/etc/passwd')
lineas = fich.readlines()
fich.close()
nlineas = len(lineas)

for linea in lineas:
    palabras = linea.split(':')
    print(palabras[0] + ': ' + palabras[-1])