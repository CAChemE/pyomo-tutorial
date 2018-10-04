# ======================================================================= #
#                     ABSTRACT MODEL EXAMPLE                              #
# ======================================================================= #

import logging
from pyomo.environ import *

'''
En ocasiones, puede ser útil dejar un modelo abstracto definido. De esa 
manera, con un rápido cambio de archivo de input, es posible darle distintos
valores a sets y parámetros.
'''

## DEFINICION DEL MODELO
# El modelo será un modelo abstracto
m = AbstractModel(name = 'Abstract Assignation')

## SETS
# Tendremos el mismo número de sets, pero no hay que iniciallizarlos
m.p = Set(ordered = True)
m.t = Set(ordered = True)

## PARAMETERS
# Habrá un parámetro
m.CI = Param(m.p,m.t,doc = 'Coeficientes de idoneidad')

## VARIABLES
# Habrá una binaria solo
m.y = Var(m.p,m.t, domain = Binary, doc = 'La persona "p" hace el trabajo "t"')

## RESTRICCIONES
# Lo de antes
# - Cada persona solo puede hacer un trabajo


def Especializacion(m, persona):
    return sum(m.y[persona, trabajo] for trabajo in m.t) == 1


m.R1 = Constraint(m.p, rule=Especializacion, doc='Una persona, un trabajo')

# - Cada trabajo solo puede hacerlo una persona


def Saturacion(m, trabajo):
    return sum(m.y[persona, trabajo] for persona in m.p) == 1


m.R2 = Constraint(m.t, rule=Saturacion, doc='Un trabajo, una persona')

## OBJETIVO
# La función objetivo es maximizar la adecuación de cada persona a su
# puesto de trabajo


def fobj(m):
    return sum(m.CI[persona, trabajo] * m.y[persona, trabajo] for persona in m.p for trabajo in m.t)

m.OBJ = Objective(rule=fobj, sense=maximize)

## DATA
# HAy que añadir los datos, claro.
inst = m.create_instance(data = 'Abstract_Data.dat')
inst.pprint()
## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(inst)
results.write() 

for i in inst.y:
    print(i, ' :', inst.y[i].value)