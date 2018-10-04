# ===================================================================== #
#                     SET COVERING PROBLEM                              #
# ===================================================================== #
import logging
from pyomo.environ import *

'''
* Source: Grado Ingeniería Química. Universidad de Alicante.
          Asignatura: Simulaicón, optimización y diseño de procesos químicos
		  
		  
El problema del set covering se basa en encontrar el menor número de conjuntos
cuya unión aun contiene a todos los elementos del universo. Es uno de los
problemas de la lista de 21 problemas NP-completos de Karp.

En este caso, consideraremos qué plantas deben ubicarse para dar servicio a
toda una zona. Cada planta dará servicio a su área y a las áreas inmediatamente
circundantes. Una imagen de las áreas está adjunta a este programa.
'''
#from os import system as sys
#sys('SC.png')

## DEFINICION DEL MODELO
# El modelo será un modelo concreto.
m = ConcreteModel()

## SETS
# Tenemos por tanto 12 zonas en total. Usaremos un set para la zona al que
# asignaremos un alias. Con esto, tendremos todo el sistema controlado.
Zonas = []
[Zonas.append('Zona ' + str(i+1)) for i in range(12)]

i = m.i = Set(initialize = Zonas, doc = 'Localizaciones', ordered = True)
j = m.j = SetOf(m.i, doc = 'Alias de localizaciones', ordered = True)

## PARÁMETROS
# El único parámetro para este problema es el que nos indica qué estaciones
# dan servicio a qué zonas. Podemos crearlo a partir de un diccionario.
v = {}
SZ = {'Zona 1': (1,2,3,5),
      'Zona 2': (1,2,5),
      'Zona 3': (1,3,4,5,6,7,8),
      'Zona 4': (3,4,5,6,11),
      'Zona 5': (1,2,3,4,5,10,11),
      'Zona 6': (3,4,6,8,11),
      'Zona 7': (3,7,8,11),
      'Zona 8': (6,7,8,9,11,12),
      'Zona 9': (8,9,10,11,12),
     'Zona 10': (5,9,10,11),
     'Zona 11': (4,5,6,8,9,10,11),
     'Zona 12': (7,8,9,12)}

for s in SZ:
    for ss in SZ[s]:
        v[s,'Zona ' + str(ss)] = 1

c = m.c = Param(m.j, m.i, initialize = v, default = 0,
              doc = 'Estación i da servicio a zona j')
# Esta es una de las posibilidades. Claramente hay varias más. Cada uno
# que coja la que le sea más cómoda.

## VARIABLES
# Deben declararse las variables del modelo. En este caso, sólo existe
# una variable, la cual es binaria.
y = m.y = Var(m.i, within = Binary, doc = 'Existe una planta en i')

## RESTRICCIONES
# Es necesario escribir las ecuaciones del modelo. En este caso, solo existe
# una restricción.
def r1(m, a):
    return sum(c[a,b]*y[b] for b in i) >= 1
R1 = m.r1 = Constraint(j, rule = r1, doc = 'Satisfacción de demanda')

## FUNCIÓN OBJETIVO
# Es necesario dar una función a minimizar
def obj(m):
    return sum(y[a] for a in i)
OBJ = m.obj = Objective(rule = obj, sense = minimize, doc = 'Número de plantas')

## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()


## LOGGING
# Se crea el logger y se da el nivel
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Se crea el formateador
formatter = logging.Formatter('%(message)s')
# Se crea lo que tratará el archivo y se le asigna el formateador
file_handler = logging.FileHandler(__file__[:-3] + '_Logging.log', mode='w')
file_handler.setFormatter(formatter)
# Se empieza a añadir cosas
logger.addHandler(file_handler)

# Creamos una función para acelerarlo:
def archivar(x, tipo='constraint'):
    parrafo = '\n{0}: {1} ----------------\n'.format(x, x.doc)
    for i in x:
        if tipo == 'constraint':
            parrafo += '\n{0}'.format(x[i].expr)
        elif tipo == 'parameter':
            parrafo += '\n{0} = {1}'.format(i, x[i])
        elif tipo == 'variable':
            parrafo += '\n{0} = {1}'.format(i, x[i].value)
    return parrafo

logger.info(results)
logger.info('\n========== OBJECTIVE FUNCTION ==========')
logger.info(OBJ.expr)
logger.info('\nEl valor de la función objetivo es: ')
logger.info(OBJ.expr())
logger.info('========================================')
logger.info('\n============== PARAMETERS ==============')
logger.info(archivar(c, tipo='parameter'))
logger.info('========================================')
logger.info('\n============== CONSTRAINTS ==============')
logger.info(archivar(R1))
logger.info('=========================================')
logger.info('\n==================================== VARIABLES ====================================')
logger.info(archivar(y, tipo='variable'))
logger.info('===================================================================================')

