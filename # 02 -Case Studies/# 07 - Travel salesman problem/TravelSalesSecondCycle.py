# ===================================================================== #
#                     TRAVEL SALESMAN PROBLEM                           #
# ===================================================================== #
import logging
from pyomo.environ import *

'''
Y aun quedan ciclos, así que se repite
'''


## DEFINICION DEL MODELO
# El modelo será un modelo concreto. 
m = ConcreteModel(name = 'Knap-sack problem')

## SETS
# Tenemos un set de ciudades y un alias de este set.
c = m.c = Set(initialize = ['A','B','C','D','E','F'], ordered = True)
cc = m.cc = SetOf(c, ordered = True)

# Añadimos sets para los ciclos:
SS1 = m.SS1 = Set(initialize = ['A','D','F'], within = c)
SS2 = m.SS2 = Set(initialize = ['B','C','E'], within = c)
SS3 = m.SS3 = Set(initialize = ['A','F'],     within = c)
SS4 = m.SS4 = Set(initialize = ['B','D'],     within = c)
SS5 = m.SS5 = Set(initialize = ['C','E'],     within = c)



# Tenemos tambien una relación que nos permite decidir que ciudades están
# comunicadas con qué ciudades.
RelDic = {'A': ('B','D','F'),
          'B': ('A','C','D','E'),
          'C': ('B','D','E','F'),
          'D': ('A','B','C','F'),
          'E': ('B','C','F'),
          'F': ('A','C','D','E','F')}

R = m.R = Set(within = c*cc, ordered = True)
for s in RelDic:
    for ss in RelDic[s]:
        R.add((s,ss))

## PARÁMETROS
# Como parámetros, tenemos las distancias entre las ciudades. A las que no existen
# pondremos un cero.
DistDic = {}
DistList = [8,3,4,8,1,5,9,1,7,2,21,3,5,7,3, 9,2,35,4,21,3,35,5]
for n,i in enumerate(R):
    DistDic[i] = DistList[n]

Cf = m.Cf = Param(c,cc, initialize = DistDic, default = 0, doc = 'Distancia entre las ciudades')

## VARIABLES
# Necesitamos una binaria que nos indique si se va de una ciudad c a una ciudad cc.
y = m.y = Var(c,cc, domain = Binary, doc = 'Indica si se hace el trayecto de "c" a "cc"')

## RESTRICCIONES
# Hay que poner las restricciones

#- De todas las ciudades, debe llegar a una
def Llegada(m,ciudad):
    return sum(y[ciudad,cciudad] for cciudad in cc if (ciudad,cciudad) in R) == 1
R1 = m.r1 = Constraint(c, rule = Llegada, doc = 'Desde todas las ciudades debe llegar a una')

#- A todas las ciudades, debe llegar a una.
def Ida(m, cciudad):
    return sum(y[ciudad,cciudad] for ciudad in c if (ciudad,cciudad) in R) == 1
R2 = m.r2 = Constraint(cc, rule = Ida, doc = 'De todas las ciudades, debe llegar de una')

# - Ruptura de ciclo 1
def Ruptura1(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS1 and cciudad not in SS1) >= 1
RC1 = m.rc1 = Constraint(rule = Ruptura1, doc = 'Romper el ciclo [A,D,F]')

# - Ruptura de ciclo 2
def Ruptura2(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS2 and cciudad not in SS2) >= 1
RC2 = m.rc2 = Constraint(rule = Ruptura2, doc = 'Romper el ciclo [B,C,E]')

# - Ruptura de ciclo 3
def Ruptura3(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS3 and cciudad not in SS3) >= 1
RC3 = m.rc3 = Constraint(rule = Ruptura3, doc = 'Romper el ciclo [A,F]')

# - Ruptura de ciclo 4
def Ruptura4(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS4 and cciudad not in SS4) >= 1
RC4 = m.rc4 = Constraint(rule = Ruptura4, doc = 'Romper el ciclo [B,D]')

# - Ruptura de ciclo 5
def Ruptura5(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS5 and cciudad not in SS5) >= 1
RC5 = m.rc5 = Constraint(rule = Ruptura5, doc = 'Romper el ciclo [C,E]')

## OBJETIVO
# El objetivo es minimizar la distancia recorrida.
def fobj(m):
    return sum(Cf[ciudad,cciudad]*y[ciudad,cciudad] for ciudad in c for cciudad in cc)
OBJ = m.obj = Objective(rule = fobj, sense = minimize, doc = 'Distancia recorrida')

## FIJAR
# Hay que fijar las que no esten en la relación a cero
for ciudad in c:
    for cciudad in cc:
        if (ciudad,cciudad) not in R:
            y[ciudad,cciudad] = 0
            y[ciudad,cciudad].fixed = True

## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()

## LECTURA DE RESULTADOS
# Para leer resultados concretos, puede hacerse lo siguiente:
print('---------- CAMINO MÁS CORTO -------------')
for i,n in enumerate(y):
    if y[n].value == 1:
        print(y[n])


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
logger.info(archivar(Cf, tipo='parameter'))
logger.info('========================================')
logger.info('\n============== CONSTRAINTS ==============')
logger.info(archivar(R1))
logger.info(archivar(R2))
logger.info(archivar(RC1))
logger.info(archivar(RC2))
logger.info(archivar(RC3))
logger.info(archivar(RC4))
logger.info(archivar(RC5))
logger.info('=========================================')
logger.info('\n==================================== VARIABLES ====================================')
logger.info(archivar(y, tipo='variable'))
logger.info('===================================================================================')
