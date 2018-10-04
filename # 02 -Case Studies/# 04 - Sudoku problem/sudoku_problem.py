"""
*-------------------------------------------------------------------------------------
*                           #### SUDOKU GAME ####
*-------------------------------------------------------------------------------------
*                                              Juan Javaloyes  & Daniel Vázquez   2018
*                                                             javaloyes.juan@gmail.com
*                                                        danielvazquez150791@gmail.com



* Based on an example written in GNU MathProg by Andrew Makhorin <mao@mai2.rcnet.ru>
* https://support.gams.com/gams:sudoku_with_gams

"""


from  pyomo.environ import *
import pandas as pd


model = ConcreteModel (name = "SUDOKU PROBLEM ")

# 01 # Read data form excel file using pandas
sudoku_data = 'sudoku_data_2'

data_df = pd.read_excel(sudoku_data + '.xlsx',   index_col = 0)

# 02 # Set declarations
row    = data_df.index.tolist()
column = data_df.columns.tolist()

r = model.r = Set(initialize = row, ordered = True)
c = model.c = Set(initialize = column, ordered = True)
k = model.k = Set(initialize = ['1', '2', '3', '4', '5', '6', '7', '8', '9'], ordered = True)

# 03 # Sudoku givens
givens = {(i,j): data_df.at[i,j] for i in r for j in c}

# 04 # Binary Variable
y = model.y = Var(r, c, k, domain = Binary)


#----------------------------------------------------------
# ### MODEL EQUATIONS ###
#----------------------------------------------------------

# 05 # Dummy objective function
model.dummy_obj = Objective(expr = 1)

# 06 # Fix binary variables corresponding with given values
for i in r:
	for j in c:
		for kk in k:
			value = int( data_df.at[i,j] == k.ord(kk) )
			if value == 1:
				y[i,j,kk].fix( 1 )


			
# Model Constraints
#==============================================================


# 07 # Only one value in each Row
def constraint_row_rule (model, rr, kk):
	return sum(y[rr,cc,kk] for cc in c ) == 1
model.constraint_row = Constraint(r, k, rule = constraint_row_rule)

# eq_02_rows(r1,1)..  y(r1,c1,1) + y(r1,c2,1) + y(r1,c3,1) + y(r1,c4,1) + y(r1,c5,1) + y(r1,c6,1) + y(r1,c7,1) + y(r1,c8,1) + y(r1,c9,1) =E= 1 ;
# eq_02_rows(r1,2)..  y(r1,c1,2) + y(r1,c2,2) + y(r1,c3,2) + y(r1,c4,2) + y(r1,c5,2) + y(r1,c6,2) + y(r1,c7,2) + y(r1,c8,2) + y(r1,c9,2) =E= 1 ;
#  ...
#eq_02_rows(r9,9)..  y(r9,c1,9) + y(r9,c2,9) + y(r9,c3,9) + y(r9,c4,9) + y(r9,c5,9) + y(r9,c6,9) + y(r9,c7,9) + y(r9,c8,9) + y(r9,c9,9) =E= 1 ;     

# 08 # Only one value in each Column
def constraint_column_rule (model, cc, kk):
	return sum(y[rr,cc,kk] for rr in r ) == 1
model.constraint_column = Constraint(c, k, rule = constraint_column_rule)

# eq_03_columns(c1,1)..  y(r1,c1,1) + y(r2,c1,1) + y(r3,c1,1) + y(r4,c1,1) + y(r5,c1,1) + y(r6,c1,1) + y(r7,c1,1) + y(r8,c1,1) + y(r9,c1,1) =E= 1 ;
# eq_03_columns(c1,2)..  y(r1,c1,2) + y(r2,c1,2) + y(r3,c1,2) + y(r4,c1,2) + y(r5,c1,2) + y(r6,c1,2) + y(r7,c1,2) + y(r8,c1,2) + y(r9,c1,2) =E= 1 ;
#  ...
# eq_03_columns(c9,9)..  y(r1,c9,9) + y(r2,c9,9) + y(r3,c9,9) + y(r4,c9,9) + y(r5,c9,9) + y(r6,c9,9) + y(r7,c9,9) + y(r8,c9,9) + y(r9,c9,9) =E= 1 ;


# 09 # Every cell in the SUDOKU must be filled with a number
def constraint_cells_rule(model, rr, cc):
	return sum ( y[rr, cc, kk] for kk in k) == 1
model.constraing_cells = Constraint(r, c, rule = constraint_cells_rule)


# 10 # Only one value in each 3x3 Grid
block = model.block = Set(initialize = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9'], ordered = True)


# > Aux Set. Relationship blocks with rows
br = model.br = Set(within = block * r, ordered = True )

br_mapping = {
              'b1': ('r1', 'r2', 'r3'), 
              'b2': ('r1', 'r2', 'r3'),
			  'b3': ('r1', 'r2', 'r3'),
			  
			  'b4': ('r4', 'r5', 'r6'),
			  'b5': ('r4', 'r5', 'r6'),
			  'b6': ('r4', 'r5', 'r6'),
			  
			  'b7': ('r7', 'r8', 'r9'),
			  'b8': ('r7', 'r8', 'r9'),
			  'b9': ('r7', 'r8', 'r9')
}

for s in br_mapping:
    for ss in br_mapping[s]:
        br.add((s, ss))
		
		
# > Aux Set. Relationship blocks with columns
bc = model.bc = Set(within = block * c, ordered = True )

bc_mapping = {
              'b1': ('c1', 'c2', 'c3'), 
              'b2': ('c4', 'c5', 'c6'),
			  'b3': ('c7', 'c8', 'c9'),
			  
              'b4': ('c1', 'c2', 'c3'), 
              'b5': ('c4', 'c5', 'c6'),
			  'b6': ('c7', 'c8', 'c9'),
			  
              'b7': ('c1', 'c2', 'c3'), 
              'b8': ('c4', 'c5', 'c6'),
			  'b9': ('c7', 'c8', 'c9'),
}

for s in bc_mapping:
    for ss in bc_mapping[s]:
        bc.add((s, ss))

# > Block definition
brc = model.brc = Set(within = block * r * c, ordered = True)

for s in br:
	for ss in bc:
		if s[0] == ss[0]:
			brc.add((s[0], s[1], ss[1]))

# > Only one value in each 3x3 Grid
def constraint_grid_rule (model, bb, kk):
	return sum( y[rr,cc,kk] for rr in r for cc in c if(bb, rr, cc) in brc ) == 1

model.constraint_grid = Constraint(block, k, rule = constraint_grid_rule)

# eq_04_grid(b1,1)..  y(r1,c1,1) + y(r1,c2,1) + y(r1,c3,1) + y(r2,c1,1) + y(r2,c2,1) + y(r2,c3,1) + y(r3,c1,1) + y(r3,c2,1) + y(r3,c3,1) =E= 1 ;
# ...
# eq_04_grid(b1,9)..  y(r1,c1,9) + y(r1,c2,9) + y(r1,c3,9) + y(r2,c1,9) + y(r2,c2,9) + y(r2,c3,9) + y(r3,c1,9) + y(r3,c2,9) + y(r3,c3,9) =E= 1 ;
# ...
# ...
# eq_04_grid(b9,9)..  y(r7,c7,9) + y(r7,c8,9) + y(r7,c9,9) + y(r8,c7,9) + y(r8,c8,9) + y(r8,c9,9) + y(r9,c7,9) + y(r9,c8,9) + y(r9,c9,9) =E= 1	  


# 11 # Call MILP Solver
SolverFactory('glpk').solve(model, tee = True)



# ======================================================================================
#---------------------------------- RESULTS --------------------------------------------
# ======================================================================================

SUDOKU = {(i,j): kk for i in r for j in c for kk in k if y[i,j,kk].value == 1 }

sudoku_sol = data_df
for i in y:
	if y[i].value == 1:
		sudoku_sol.at[i[0], i[1]] = i[2]
	

print(sudoku_sol)

sudoku_sol.to_excel(sudoku_data + '_sol.xlsx')
