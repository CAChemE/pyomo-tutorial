"""
*-------------------------------------------------------------------------------------
*                           #### STRIP-PACKING 2D PROBLEM ####
**------------------------------------------------------------------------------------
*                                                           Juan Javaloyes     2018
*                                                           javaloyes.juan@gmail.com


* N.W. Sawaya, I. E. Grossmann. "A cutting plane method for solving linear generalized 
  disjunctive programming problems". 2005
* http://cepac.cheme.cmu.edu/pasi2008/slides/vecchietti/library/reading/SawayaCuttingCACE.pdf

"""


"""
 PROBLEM STATMENT:
    A given set of rectangles is to be packed into a strip of fixed width W 
    but unknown length L. The objective is to minimize the length of the 
    strip while fitting all rectangles without overlap and without rotation.
	
	This is combinatorial NP-hard optimization problem.
"""


from  pyomo.environ import *
import pandas as pd
import numpy as np


model = ConcreteModel (name = "STRIP-PACKING 2D PROBLEM ")

# 01 # Read data form excel file using pandas
excel_filename = 'strip_packing_2D_data.xlsx';

sp2d_df = pd.read_excel(excel_filename,   skiprows = 3, parse_cols = 'B:D', skip_footer = 0, index_col = 0, header = 0)


# 02 # Set declarations
rectangle_i = sp2d_df.index.tolist()
I = model.I = Set(initialize = rectangle_i, ordered = True)
J = model.J = Set(initialize = rectangle_i, ordered = True)


# 03 # Rectangle dimensions (Length & Height)
L = {k: sp2d_df.at[k, 'L'] for k in I} 
H = {k: sp2d_df.at[k, 'H'] for k in I} 

L_up = sp2d_df['L'].sum() # Total Length if all the rectangles are stacked together 

# 04 # Parameter declarations

# > Width of the strip
width_strip = sp2d_df['H'].max()
W = width_strip

# Big-M parameter
M1 = 70 
M2 = 70 
M3 = 60 
M4 = 60 


# 05 # Decision Variables or Independent Variables Declaration
# Continuous Variables
lt = model.lt = Var(   domain = NonNegativeReals, doc = 'Length of the strip') 
x  = model.x  = Var(I, domain = NonNegativeReals, doc = 'x axis position' )
y  = model.y  = Var(I, domain = NonNegativeReals, doc = 'y axis position')
 
	
# Binary Variables
w1 = model.w1 = Var(I,J, domain = Binary)
w2 = model.w2 = Var(I,J, domain = Binary)
w3 = model.w3 = Var(I,J, domain = Binary)
w4 = model.w4 = Var(I,J, domain = Binary)

#----------------------------------------------------------
# ### MODEL EQUATIONS ###
#----------------------------------------------------------

# 06 # Objective function. Length of the strip
model.objective_fcn = Objective(expr = lt, sense = minimize)


# 07 # Global Constraint. 
def global_constraint_rule (model, i):
	return lt >= x[i] + L[i]
model.global_constraint = Constraint(I, rule = global_constraint_rule)

# 08 # Disjunctions. Big-M Reformulation 
# Each disjunct represents the position of rectangle i in relation to rectangle j
# The point of  reference (xi, yi)  corresponds  to  the  upper  left  corner  of  every rectangle

# > Disjunction <1>
def disjunction_1_rule (model, i, j):
	if i < j:
		return x[i] + L[i] <= x[j] + M1 * (1 - w1[i,j])
	else:
		return Constraint.Skip
model.disjunction_1 = Constraint(I, J, rule = disjunction_1_rule)


# > Disjunction <2>
def disjunction_2_rule (model, i, j):
	if i < j:
		return x[j] + L[j] <= x[i] + M2 * (1 - w2[i,j])
	else:
		return Constraint.Skip
model.disjunction_2 = Constraint(I, J, rule = disjunction_2_rule)


# > Disjunction <3>
def disjunction_3_rule (model, i, j):
	if i < j:
		return y[i] - H[i] >= y[j] - M3 * (1 - w3[i,j])
	else:
		return Constraint.Skip
model.disjunction_3 = Constraint(I, J, rule = disjunction_3_rule)

# > Disjunction <4>
def disjunction_4_rule (model, i, j):
	if i < j:
		return y[j] - H[j] >= y[i] - M4 * (1 - w4[i,j])
	else:
		return Constraint.Skip
model.disjunction_4 = Constraint(I, J, rule = disjunction_4_rule)

# 09 # 
def logic_proposition_rule (model, i, j):
	if i < j:
		return w1[i,j] + w2[i,j] + w3[i,j] + w4[i,j] == 1
	else:
		return Constraint.Skip
model.logic_proposition = Constraint(I, J, rule = logic_proposition_rule)


# 10 # x-coordinate upper bound for every rectangle
x_UP =  L_up

for i in I:
    x[i].setub(x_UP - L[i])
	 

# 10 # y-coordinate upper and lower bounds
for i in I:
	y[i].setub(W)
	y[i].setlb(H[i])
	
	
# 12 # Call MILP Solver
SolverFactory("glpk").solve(model, tee = True)


# 13 # Plot Results ===========================================================

xi_array = np.array([])
yi_array = np.array([])
Li_array = np.array([])
Hi_array = np.array([])

for i in I:
	xi = x[i].value
	yi = y[i].value
	Li = L[i]
	Hi = H[i]
	xi_array = np.append(xi_array, xi)
	yi_array = np.append(yi_array, yi)
	Li_array = np.append(Li_array, Li)
	Hi_array = np.append(Hi_array, Hi)

xi_array = xi_array.reshape(1, np.shape(xi_array)[0])
yi_array = yi_array.reshape(1, np.shape(yi_array)[0])

	
Xi_array = np.vstack((xi_array, xi_array + Li_array, xi_array + Li_array, xi_array))	
Yi_array = np.vstack((yi_array, yi_array           , yi_array - Hi_array, yi_array - Hi_array))	
	
import matplotlib.pyplot as plt	
	
p1 = plt.fill(Xi_array, Yi_array)	
plt.show()

	
	
	
	
	
	
	
	
	
	
