# -- Creamos las variables --
Entero = 8
Real = 4
Nombre = ['Christian Abad González']
Asig1cuatri = ['PTAVI', 'CyS', 'CyO', 'IA2']
Asig2cuatri = ['SCA', 'CSAI', 'ESAV', 'ECAV']
Asigpendientes = ['IM', 'FDM', 'EA', 'TDS', 'CIA', 'TDI', '3D', 'LTA', 'TTI' 'ASA2', 'TFG', 'PE', 'RAC']

# -- Imprimimos las variables por separado --
print(Entero)
print()

print(Real)
print()

print(Nombre)
print()

print(Asig1cuatri)
print()

print(Asig2cuatri)
print()


print("El alumno: " + str(Nombre) + ',' + " tiene este curso: " + str(Entero) + " asignaturas, las cuales están divididas\n"
" en: " + str(Real) + " asignaturas por cuatrimestre que son: " + str(Asig1cuatri[:-1]) + ' y ' + str(Asig1cuatri[-1]) + " en\n"
" el primer cuatrimestre" + " y " + str(Asig2cuatri[:-1]) + " y " + str(Asig2cuatri[3]) + " , " + " en el segundo cuatrimestre.\n"
" Aparte de estas asignaturas le quedan pendientes " + " las siguientes asignaturas:\n" + str(Asigpendientes[:-1]) + 'y' + str(Asigpendientes[-1]) + ". Buff, que ganas.")