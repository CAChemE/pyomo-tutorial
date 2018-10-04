# ===================================================================== #
#                     KNAPS-SACK PROBLEM                                #
# ===================================================================== #
import logging
from pyomo.environ import *

'''
* Source: Grado Ingeniería Química. Universidad de Alicante.
          Asignatura: Simulaicón, optimización y diseño de procesos químicos
		  

El problema de la mochila, oomunmente abreviado como KP problem, es un
problema de optimización combinatoria. Al igual que el del Set-Covering,
es uno de los 21 problemas NP-completos de Richard Karp.

En este ejemplo, somos un ladrón y tenemos un camello (O un caballo.
Depende de la preferencia personal de cada uno) con una capacidad de
2000 cm3. Después de diferentes pruebas se determinó que el máximo de
masa que sería capaz de cargar es de 2500 gramos. La lista de objetos
posibles a robar son los siguientes.

#============== TABLA DE OBJETOS ============================
                      Precio   Volumen  Peso unidad   Número
cofre                   50      1000    2000            1
anillo                   5        2       20           10
collar                   3       10      300            1
espejo                  20      500     1000            1
brazaletes              16       15      300           15
sortija con rubí         5        3       75            1
frasco perfume           1      100      100            1
diamante                30        5       50            1
copa de oro             12      250      500            1
Bote azafrán            40      100      100            1
# ===========================================================

¿Qué sería lo mejor que podríamos llevarnos sin acabar teniendo que cargar
con un cabello? (O un camallo)
'''

## DEFINICION DEL MODELO
# El modelo será un modelo concreto.
m = ConcreteModel(name='Knap-sack problem')

## SETS
# Tenemos un set de objetos.
Objetos = []
[Objetos.append('Objeto ' + str(i + 1)) for i in range(10)]
obj = m.obj = Set(initialize=Objetos, doc='Objetos', ordered=True)

## PARAMETERS
# Hacemos las listas de cada valor y inicializamos los diccionarios.
PrecioDic = {}
PreciosList = [50, 5, 3, 20, 16, 5, 1, 30, 12, 40]
VolumenDic = {}
VolumenList = [1000, 2, 10, 500, 15, 3, 100, 5, 250, 100]
PesosDic = {}
PesosList = [2000, 20, 300, 1000, 300, 75, 100, 50, 500, 100]
NumeroDic = {}
NumeroList = [1, 10, 1, 1, 15, 1, 1, 1, 1, 1]
# Rellenamos los diccionarios
for i in range(len(PreciosList)):
    PrecioDic[Objetos[i]] = PreciosList[i]
    VolumenDic[Objetos[i]] = VolumenList[i]
    PesosDic[Objetos[i]] = PesosList[i]
    NumeroDic[Objetos[i]] = NumeroList[i]
# Creamos los parámetros
MP = m.MP = Param(obj, initialize=PrecioDic,  doc='Precio de mercado')
V  = m.V  = Param(obj, initialize=VolumenDic, doc='Volumen unidad')
W  = m.W  = Param(obj, initialize=PesosDic,   doc='Peso unidad')
N  = m.N  = Param(obj, initialize=NumeroDic,  doc='Número de unidades existentes')

## VARIABLES
# Necesitamos dos variables. Una binaria que nos diga siguientes
# elegimos el objeto o no, y una variable entera positiva que nos indique
# el número de objetos de cada uno que nos llevamos.
y = m.y = Var(obj, domain=Binary, doc='Elegimos el objeto "obj"')
n = m.n = Var(obj, domain=NonNegativeIntegers, doc='Cogemos "n" objetos "obj"')

## RESTRICCIONES
# Escribimos las restricciones necesarias.
# - Debe cumplirse la restricción de volumen


def VolumeRule(m):
    return sum(V[i] * n[i] for i in obj) <= 2000


R1 = m.VolumeRule = Constraint(rule=VolumeRule, doc = 'Restricción de volumen')

# - Debe cumplirse la restricción de peso


def WeightRule(m):
    return sum(W[i] * n[i] for i in obj) <= 2500


R2 = m.WeightRule = Constraint(rule=WeightRule, doc = 'Restricción de peso')

# - No puedes coger mas objetos de los que hay


def NumberRule(m, i):
    return n[i] <= N[i]


R3 = m.NumberRule = Constraint(obj, rule=NumberRule, doc = 'De donde no hay no se puede sacar')

## OBJETIVO
# El objetivo es maximizar los beneficios obtenidos del hurto y no romper
# la columna del camello en el proceso. Por tanto, la función objetivo se
# referirá a los beneficios obtenidos


def ObjFunc(m):
    return sum(MP[i] * n[i] for i in obj)


OBJ = m.objective = Objective(rule=ObjFunc, sense=maximize, doc='Beneficio')

## VERBATIM DE RESOLUCIÓN
from pyomo.opt import SolverFactory
opt = SolverFactory('glpk')
results = opt.solve(m)
results.write()

## LECTURA DE RESULTADOS
# Para leer resultados concretos, puede hacerse lo siguiente:
for i in obj:
    print('De ', i, 'se cogen ', n[i].value)


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
logger.info(archivar(MP, tipo='parameter'))
logger.info(archivar(V, tipo='parameter'))
logger.info(archivar(W, tipo='parameter'))
logger.info(archivar(N, tipo='parameter'))
logger.info('========================================')
logger.info('\n============== CONSTRAINTS ==============')
logger.info(archivar(R1))
logger.info(archivar(R2))
logger.info(archivar(R3))
logger.info('=========================================')
logger.info('\n==================================== VARIABLES ====================================')
logger.info(archivar(n, tipo='variable'))
logger.info('===================================================================================')
