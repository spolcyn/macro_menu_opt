import pulp
import pandas as pd

def premadesalad_selection(P, C, F):

    # import nutritional csv
    menu = pd.read_csv('./sweetgreen_PP.csv')
    menu = menu.dropna()

    # set solver
    solver = pulp.getSolver('GUROBI')

    # pull out the premade salads
    salads = menu[menu['Category'] == 'SALADS'].copy()

    # Instantiate the model
    model = pulp.LpProblem("MacroModel", pulp.LpMinimize)

    # Set variable names
    salad_names = list(salads['Name'])

    # Set decision variables as Binary 0 or 1
    x = pulp.LpVariable.dicts("x", salad_names, cat='Binary')

    # Build objective function
    zp = dict(zip(salad_names, salads['Protein (g)']))  # protein
    zc = dict(zip(salad_names, salads['Total Carbs (g)']))  # carbs
    zf = dict(zip(salad_names, salads['Total Fat (g)']))  # fats
    zfiber = dict(zip(salad_names, salads['Fiber (g)']))  # fiber
    zsodium = dict(zip(salad_names, salads['Sodium (mg)']))  # sodium
    zsugar = dict(zip(salad_names, salads['Sugars (g)']))  # sugar
    # - zfiber[i] + zsugar[i] + zsodium[i] / 100
    # Set Objective Function:
    model += (P + C + F) - pulp.lpSum([(zp[i] + zc[i] + zf[i]) * x[i] for i in salad_names])

    # Add Constraints
    model += pulp.lpSum([x[i] for i in salad_names]) == 1, 'Salad Limit'
    model += pulp.lpSum([(x[i] * zp[i]) for i in salad_names]) <= P, 'Protein Max'
    model += pulp.lpSum([(x[i] * zc[i]) for i in salad_names]) <= C, 'Carb Max'
    model += pulp.lpSum([(x[i] * zf[i]) for i in salad_names]) <= F, 'Fat Max'

    return model
def pm_postprocess(model):
    #Print Status
    print(pulp.LpStatus[model.status])
    print(pulp.value(model.objective))

    #Print decision variables and get name of chosen salad
    for i,v in enumerate(model.variables()):
        if(v.varValue > 0):
            print(v.name, "=", v.varValue)
            name = v.name.split('x_')[1].replace("_", " ")

    return name
