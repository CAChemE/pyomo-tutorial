"""
*-------------------------------------------------------------------------------------
*                           #### MACHINERY PROBLEM ####
**------------------------------------------------------------------------------------
*                                                           Juan Javaloyes     2018
*                                                           javaloyes.juan@gmail.com


* Source: Grado Ingeniería Química. Universidad de Alicante.
          Asignatura: Simulaicón, optimización y diseño de procesos químicos

"""


"""
 PROBLEM STATMENT:
    A company manufacture four types of machinery. The factory is divided in three sections.
	The first section has available 960 h/week, the second 1110 h/week and the third 400 h/week.
	Each machinery unit requires the time given in "time_x_section" at each section.
	Determine the number of units of machinery for each type that should be manufacture per week
	to maximize profit.
"""

from pyomo.environ import *
m = ConcreteModel()

M = m.M = Set(initialize =  ['m1', 'm2', 'm3', 'm4'], ordered = True)
S = m.S = Set(initialize =  ['s1', 's2', 's3'], ordered = True)

profit   = {'m1':  12, 'm2':    8, 'm3':  12, 'm4':17}
max_time = {'s1': 960, 's2': 1110, 's3': 400}

time_x_section = { ('m1','s1'): 6 , ('m1','s2'): 3 , ('m1','s3'): 2,
                   ('m2','s1'): 4 , ('m2','s2'): 3 , ('m2','s3'): 1,
				   ('m3','s1'): 4 , ('m3','s2'): 6 , ('m3','s3'): 2,
				   ('m4','s1'): 8 , ('m4','s2'): 9 , ('m4','s3'): 1}

x = m.x = Var( M, within = PositiveIntegers )

m.value = Objective( expr = sum( profit[i] * m.x[i] for i in M),
                     sense = maximize )

					 

def constraint_rule(m, j):
	return sum( time_x_section[i,j] * x[i] for i in M) <= max_time[j]
m.constraint = Constraint(S, rule = constraint_rule) 
						  						  

SolverFactory('glpk').solve(m, tee = True)

m.pprint()