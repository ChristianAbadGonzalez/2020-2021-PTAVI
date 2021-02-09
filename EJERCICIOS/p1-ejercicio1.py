#--Creamos las variables
Entero = 10
Real = -5
Cadena = 'Cristina'
Lista = ['ptavi', 'tds', 'asa2', 'ia2']
Asig_pendientes = ['tfg', 'practicas', 'ptavi', 'tds', 'asa2', 'ia2', 'equipos', 'tti', 'laboratorio', 'difusion']

#--Imprimimos las variables
print(Entero)
print()

print(Real)
print()

print(Cadena)
print()

for Asig in Lista:
    print(Asig)

print()

print("Me quedan ", len(Asig_pendientes), " asignaturas para acabar la carrera. Son ", Asig_pendientes[0],",",
      Asig_pendientes[1],",", Asig_pendientes[2],",", Asig_pendientes[3],",", Asig_pendientes[4],",", Asig_pendientes[5],
      ",",Asig_pendientes[6],",", Asig_pendientes[7],",", Asig_pendientes[8], ',', Asig_pendientes[9],".Buff, ¡qué ganas!")
print()

#-- Imprimimos la cadena y los elementos de la lista mostrando sus longitudes.
print(Cadena, len(Cadena))

for Asig in Lista:
    print(Asig, len(Asig))

for Pendientes in Asig_pendientes:
    print(Pendientes, len(Pendientes))

print()

#-- Imprimimo el tercer caracter de mi nombre que se encuentra guardado en la variable Cadena.
print("El tercer caracter de mi nombre es: ", Cadena[2])


