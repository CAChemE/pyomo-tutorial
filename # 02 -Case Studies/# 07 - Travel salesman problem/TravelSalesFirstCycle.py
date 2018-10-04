# ===================================================================== #
#                     TRAVEL SALESMAN PROBLEM                           #
# ===================================================================== #

from pyomo.environ import *

'''
Como vimos antes, se produjeron dos ciclos. Estos son:
  A->D->F->A  y  B->C->E->B
A menos que nuestro viajante tenga la capacidad de la 
teletransportación instantánea, estos ciclos deben romperse.
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

Cf = m.Cf = Param(c,cc, initialize = DistDic, default = 0)

## VARIABLES
# Necesitamos una binaria que nos indique si se va de una ciudad c a una ciudad cc.
y = m.y = Var(c,cc, domain = Binary)

## RESTRICCIONES
# Hay que poner las restricciones

#- De todas las ciudades, debe llegar a una
def Llegada(m,ciudad):
    return sum(y[ciudad,cciudad] for cciudad in cc if (ciudad,cciudad) in R) == 1
R1 = m.r1 = Constraint(c, rule = Llegada)

#- A todas las ciudades, debe llegar a una.
def Ida(m, cciudad):
    return sum(y[ciudad,cciudad] for ciudad in c if (ciudad,cciudad) in R) == 1
R2 = m.r2 = Constraint(cc, rule = Ida)

# - Ruptura de ciclo 1
def Ruptura1(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS1 and cciudad not in SS1) >= 1
RC1 = m.rc1 = Constraint(rule = Ruptura1)

# - Ruptura de ciclo 2
def Ruptura2(m):
    return sum(y[ciudad,cciudad] for ciudad in c for cciudad in cc if ciudad in SS2 and cciudad not in SS2) >= 1
RC2 = m.rc2 = Constraint(rule = Ruptura2)



## OBJETIVO
# El objetivo es minimizar la distancia recorrida.
def fobj(m):
    return sum(Cf[ciudad,cciudad]*y[ciudad,cciudad] for ciudad in c for cciudad in cc)
OBJ = m.obj = Objective(rule = fobj, sense = minimize)


## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()


