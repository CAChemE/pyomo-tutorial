# ======================================================================= #
#                     ASSIGNATION PROBLEM                             #
# ======================================================================= #

import logging
from pyomo.environ import *

'''
* Source: Grado Ingeniería Química. Universidad de Alicante.
          Asignatura: Simulaicón, optimización y diseño de procesos químicos

		  
El problema de asignación es un problema de optimización combinatoria. En
el, se intenta dar solución a la asignación de un número de tareas a un
número de agentes, intentando maximizar la efectividad de las mismas.
Así, cada agente tendrá una afinidad/idoneidad por cada tarea.
'''

## DEFINICION DEL MODELO
# El modelo será un modelo concreto.
m = ConcreteModel(name='Assignation problem')

## SETS
# Tendremos dos sets. Uno de personas y uno de tareas
p = m.p = Set(initialize=['Pedro', 'Marta', 'Laura'], ordered=True)
t = m.t = Set(initialize=['Contable', 'Director de ventas', 'Recursos humanos'], ordered=True)

## PARAMETERS
# Tenemos un parámetro. El coeficiente de idoneidad.
Coeffs = {'Pedro': (11, 5, 2),
          'Marta': (15, 12, 8),
          'Laura': (3, 1, 10)}
CoeffDic = {}
for s in p:
    for ss, sss in enumerate(t):
        CoeffDic[s, sss] = Coeffs[s][ss]
CI = m.CI = Param(p, t, initialize=CoeffDic, doc='Coeficiente de idoneidad')

## VARIABLES
# Necesitamos una binaria que nos indique a qué persona se asigna
# qué trabajo.
y = m.y = Var(p, t, domain=Binary, doc = 'La persona "p" hace el trabajo "t"')

## RESTRICCIONES
# Necesitamos las siguientes restricciones
# - Cada persona solo puede hacer un trabajo
def Especializacion(m, persona):
    return sum(y[persona, trabajo] for trabajo in t) == 1


R1 = m.R1 = Constraint(p, rule=Especializacion, doc='Una persona, un trabajo')

# - Cada trabajo solo puede hacerlo una persona
def Saturacion(m, trabajo):
    return sum(y[persona, trabajo] for persona in p) == 1


R2 = m.R2 = Constraint(t, rule=Saturacion, doc='Un trabajo, una persona')

## OBJETIVO
# La función objetivo es maximizar la adecuación de cada persona a su
# puesto de trabajo


def fobj(m):
    return sum(CI[persona, trabajo] * y[persona, trabajo] for persona in p for trabajo in t)


OBJ = m.OBJ = Objective(rule=fobj, sense=maximize)

## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()


## TRATAMIENTO DE RESULTADOS
OBJ.display()

print('\n\nEl valor de las variables es:')
y.display()

print('\n\nPodemos asignar el valor del resultado a una variable')
Laura_contable = y['Laura', 'Contable'].value
print('Variable de si Laura es contable: ', Laura_contable)
FuncionObjetivo = OBJ.expr
print('La función objetivo se expresa como:\n ', FuncionObjetivo)
ValorFO = OBJ.expr()
print('El valor de la función objetivo es: ', ValorFO)

print('\nTambién se pueden ver las restricciones')
R2.pprint()
print('\nAsí como el valor de una determinada restricción')
a = R2['Contable'].expr
print(a)

## LOGGING DE RESULTADOS
# Se crea el logger y se da el nivel
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Se crea el formateador
formatter = logging.Formatter('%(message)s')
# Se crea lo que tratará el archivo y se le asigna el formateador
file_handler = logging.FileHandler('Assignment.log', mode='w')
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



# logging.basicConfig(filename='Assignment.log',
#                     filemode='w',
#                     format='%(message)s',
#                     level=logging.DEBUG)
logger.info(results)
logger.info('\n========== OBJECTIVE FUNCTION ==========')
logger.info(OBJ.expr)
logger.info('\nEl valor de la función objetivo es: ')
logger.info(OBJ.expr())
logger.info('========================================')
logger.info('\n============== PARAMETERS ==============')
# logger.info('\nCI: {0} --------------\n'.format(CI.doc))
# for i in CI:
#     logger.info('{0}, {1} = {2}'.format(i[0], i[1], CI[i]))
logger.info(archivar(CI, tipo='parameter'))
logger.info('========================================')
logger.info('\n============== CONSTRAINTS ==============')
# logger.info('\nR1: {0} --------------\n'.format(R1.doc))
# for i in R1:
#     logger.info(R1[i].expr)
# logger.info('\nR2: {0} --------------\n'.format(R2.doc))
# for i in R2:
#     logger.info(R2[i].expr)
logger.info(archivar(R1))
logger.info(archivar(R2))
logger.info('=========================================')
logger.info('\n==================================== VARIABLES ====================================')
logger.info(archivar(y, tipo='variable'))
logger.info('===================================================================================')
