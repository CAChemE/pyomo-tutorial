"""
------------------------------------------------------------------------------------
                 ####  EXAMPLE - TRANSPORT LP #####
------------------------------------------------------------------------------------
*                                                           Juan Javaloyes     2018
*                                                           javaloyes.juan@gmail.com

* Source: "A GAMS Tutorial" by Richard E. Rosenthal (2007)
http://www.un.org/en/development/desa/policy/mdg_workshops/training_material/gams_users_guide.pdf

"""



from six import iteritems
from  pyomo.environ import *


m = ConcreteModel()

""" # 01 # Set declarations"""
# Plants
I = m.I = Set( initialize = ['seattle', 'san-diego'], doc = "canning plants")

# Markets
J = m.J = Set( initialize = ['new-york', 'chicago', 'topeka'], doc = "markets")



""" # 02 # Parameters"""
# Capacity of plant i in cases
capacity_plant = {'seattle': 350, 'san-diego': 550}

a = m.a = Param(I, initialize = capacity_plant, doc = 'capacity of plant i in cases')

# Demand at market j in cases
market_demand = {'new-york': 325, 'chicago': 300, 'topeka': 275}
b = m.b = Param(J, initialize = market_demand, doc = 'demand at market j in cases')

# Distance in thousand of miles
distance = {
    ('seattle',  'new-york') : 2.5,
    ('seattle',  'chicago')  : 1.7,
    ('seattle',  'topeka')   : 1.8,
    ('san-diego','new-york') : 2.5,
    ('san-diego','chicago')  : 1.8,
    ('san-diego','topeka')   : 1.4,
}

d = m.d = Param(I, J, initialize = distance, doc = 'distances in thousand of miles')

# Transport cost in thousand of dollars per case

def trans_cost(m, i, j):
	return 90 * m.d[i,j]/1000
c = m.c = Param(I, J, initialize = trans_cost, doc = 'transport cost in thousand of dollars per case')


""" # 03 # Variable declarations"""
# Shipment quantities in cases
x = m.x = Var(I, J, domain = NonNegativeReals, doc = 'shipment quantities in cases' )


"""
----------------------------------------------------------------------------
# 04 # MODEL EQUATIONS
----------------------------------------------------------------------------
"""
# Supply limit at plant i

def supply_rule(m, i):
	return sum(m.x[i,j] for j in J) <= m.a[i]
m.supply = Constraint(I, rule = supply_rule, doc = 'supply limit at plant i')

#@m.Constraint(I, doc='supply limit at plant i')
#def supply(m, i):
#	return sum(m.x[i,j] for j in J) <= m.a[i]

# Satisfy demand at market j
def demand_rule(m, j):
	return sum(m.x[i,j] for i in I) >= m.b[j]
m.demand = Constraint(J, rule = demand_rule, doc = 'satisfy demand at market j')


""" # 05 # Transport Costs (Objective function)"""
def objective_rule(m):
	return sum(m.c[i,j] * m.x[i,j] for i in I for j in J)
m.Cost = Objective(rule = objective_rule,
				     sense = minimize)



""" # 06 # Solver Call"""
SolverFactory("glpk").solve(m, tee=True)
m.display()
