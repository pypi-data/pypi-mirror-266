import mipx

model = mipx.Model(solver_id="CPLEX")
x = model.addVar(ub=10, name='x')
y = model.addVar(ub=11, name='y')
model.addConstr(x+y >= 15)
model.setObjective(y)
status = model.optimize()
if status == mipx.OptimizationStatus.OPTIMAL:
    print("objective is ", model.ObjVal)
