import pulp
import pandas as pd
from premade_salad_opt import *
from byo_salad_opt import *
from full_menu_model import *

if __name__ == '__main__':
    #import nutritional csv
    menu = pd.read_csv('./sweetgreen_PP.csv')
    menu = menu.dropna()

    #set solver
    solver = pulp.getSolver('GUROBI')

    #Set Macro limits
    P = 67
    C = 120
    F = 87

    #run premade salad model
    premade_model = premadesalad_selection(P, C, F)

    # Solve model
    # set solver
    solver = pulp.getSolver('GUROBI')

    premade_model.solve(solver)

    #postprocess pm solution
    premade_solution = pm_postprocess(premade_model)

    # run build your own BYO salad model
    byo_model = byo_salad_model(P, C, F)

    # Solve model
    byo_model.solve(solver)

    # postprocess pm solution
    byo_solution = byo_postprocess(byo_model)

    #Full Model
    full_model = full_menu_model(P, C, F)
    full_model.solve(solver)
    full_solution = full_postprocess(full_model)
    if full_solution == 'BYO':
        solution = byo_solution
    else:
        solution = premade_solution

    # Parse out the Overall solution then condense it down to one salad
    result = menu[menu['Name'].isin(solution)].copy()
    condensed_result = pd.DataFrame(result.iloc[:, 2:].sum()).T
    rP = condensed_result['Protein (g)'].sum()
    rC = condensed_result['Total Carbs (g)'].sum()
    rF = condensed_result['Total Fat (g)'].sum()

    print('Final Salad:', solution)

    print("Target Protein: {}  "
          "Salad Protein: {}  "
          "Remaining Protein: {}".format(P, rP, P - rP))
    print("Target Carbs: {}  "
          "Salad Carbs: {}  "
          "Remaining Carbs: {}".format(C, rC, C - rC))
    print("Target Fat: {}  "
          "Salad Fat: {}  "
          "Remaining Fat: {}".format(F, rF, F - rF))