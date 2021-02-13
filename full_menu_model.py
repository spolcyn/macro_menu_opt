import pulp
import pandas as pd
from premade_salad_opt import *
from byo_salad_opt import *

def full_menu_model(P, C, F):
    # import nutritional csv
    menu = pd.read_csv('./sweetgreen_PP.csv')
    menu = menu.dropna().reset_index(drop = True)

    # set solver
    solver = pulp.getSolver('GUROBI')

    #Start by getting the best premade salad
    premade_model = premadesalad_selection(P, C, F)
    premade_model.solve(solver)
    premade_solution = pm_postprocess(premade_model)

    #Parse out winning premade salad and save for later
    pm = menu[menu['Name'] == premade_solution].copy()

    # run build your own BYO salad model
    byo_model = byo_salad_model(P, C, F)
    byo_model.solve(solver)
    byo_solution = byo_postprocess(byo_model)

    #Parse out the BYO solution then condense it down to one salad
    byo = menu[menu['Name'].isin(byo_solution)].copy()
    condensed_byo = pd.DataFrame(byo.iloc[:,2:].sum()).T
    condensed_byo['Name'] = 'BYO'
    condensed_byo['Category'] = 'BYO'

    #combine the two leading contenders
    full_menu = pm.append(condensed_byo)

    # Instantiate the full model
    model = pulp.LpProblem("MacroModel", pulp.LpMinimize)

    # Set variable names
    salad_names = list(full_menu['Name'])

    # Set decision variables as Binary 0 or 1
    x = pulp.LpVariable.dicts("x", salad_names, cat='Binary')

    # Build objective function
    zp = dict(zip(salad_names, full_menu['Protein (g)']))  # protein
    zc = dict(zip(salad_names, full_menu['Total Carbs (g)']))  # carbs
    zf = dict(zip(salad_names, full_menu['Total Fat (g)']))  # fats
    zfiber = dict(zip(salad_names, full_menu['Fiber (g)']))  # fiber
    zsodium = dict(zip(salad_names, full_menu['Sodium (mg)']))  # sodium
    zsugar = dict(zip(salad_names, full_menu['Sugars (g)']))  # sugar
    # - zfiber[i] + zsugar[i] + zsodium[i] / 100
    # Set Objective Function:
    model += (P + C + F) - pulp.lpSum([(zp[i] + zc[i] + zf[i]) * x[i] for i in salad_names])

    # Add Constraints
    model += pulp.lpSum([x[i] for i in salad_names]) == 1, 'Salad Limit'
    model += pulp.lpSum([(x[i] * zp[i]) for i in salad_names]) <= P, 'Protein Max'
    model += pulp.lpSum([(x[i] * zc[i]) for i in salad_names]) <= C, 'Carb Max'
    model += pulp.lpSum([(x[i] * zf[i]) for i in salad_names]) <= F, 'Fat Max'

    return model

def full_postprocess(model):
    #Print Status
    print(pulp.LpStatus[model.status])

    #Print decision variables and get name of chosen salad
    for i,v in enumerate(model.variables()):
        if(v.varValue > 0):
            print(v.name, "=", v.varValue)
            name = v.name.split('x_')[1].replace("_", " ")


    return name