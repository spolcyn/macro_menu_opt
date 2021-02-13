import pulp
import pandas as pd

def byo_salad_model(P, C, F):
    # import nutritional csv
    menu = pd.read_csv('./sweetgreen_PP.csv')
    menu = menu.dropna().reset_index(drop = True)

    # set solver
    solver = pulp.getSolver('GUROBI')

    # pull out the build your own ingredients
    ingredients = menu[menu['Category'] != 'SALADS'].copy()

    # Instantiate the model
    model = pulp.LpProblem("MacroModel", pulp.LpMinimize)

    # Set variable names
    indices = list(zip(ingredients.Category, ingredients.Name))

    # Set decision variables as Binary 0 or 1
    x = pulp.LpVariable.dicts("x", indices, cat='Binary')

    # Build objective function
    zp = dict(zip(indices, ingredients['Protein (g)']))  # protein
    zc = dict(zip(indices, ingredients['Total Carbs (g)']))  # carbs
    zf = dict(zip(indices, ingredients['Total Fat (g)']))  # fats
    zfiber = dict(zip(indices, ingredients['Fiber (g)']))  # fiber
    zsodium = dict(zip(indices, ingredients['Sodium (mg)']))  # sodium
    zsugar = dict(zip(indices, ingredients['Sugars (g)']))  # sugar

    # - zfiber[i] + zsugar[i] + zsodium[i] / 100
    # Set Objective Function:
    model += (P + C + F) - pulp.lpSum([(zp[i] + zc[i] + zf[i]) * x[i] for i in indices])

    # Add Constraints
    model += pulp.lpSum([(x[i] * zp[i]) for i in indices]) <= P, 'Protein Max'
    model += pulp.lpSum([(x[i] * zc[i]) for i in indices]) <= C, 'Carb Max'
    model += pulp.lpSum([(x[i] * zf[i]) for i in indices]) <= F, 'Fat Max'

    br = [(k[0],k[1]) for k, v in x.items() if k[0] == 'BREAD']
    model += pulp.lpSum([x[(i,j)] for i,j in br]) <= 1, 'Bread Limit'

    bs = [(k[0], k[1]) for k, v in x.items() if k[0] == 'BASES']
    model += pulp.lpSum([x[(i, j)] for i, j in bs]) <= 2, 'Base max'
    model += pulp.lpSum([x[(i, j)] for i, j in bs]) >= 1, 'Base min'

    ing = [(k[0], k[1]) for k, v in x.items() if k[0] == 'INGREDIENTS']
    model += pulp.lpSum([x[(i, j)] for i, j in ing]) <= 4, 'Ingredient Limit'

    pr = [(k[0], k[1]) for k, v in x.items() if k[0] == 'PREMIUMS']
    model += pulp.lpSum([x[(i, j)] for i, j in pr]) <= 2, 'Premium Limit'

    dr = [(k[0], k[1]) for k, v in x.items() if k[0] == 'DRESSINGS']
    model += pulp.lpSum([x[(i, j)] for i, j in dr]) <= 2, 'Dressing Limit'

    bv = [(k[0], k[1]) for k, v in x.items() if k[0] == 'BEVERAGES']
    model += pulp.lpSum([x[(i, j)] for i, j in bv]) <= 1, 'Beverages Limit'

    return model

def byo_postprocess(model):
    #Print Status
    print(pulp.LpStatus[model.status])

    #Print decision variables and get name of chosen ingredients
    solution = list()
    for v in model.variables():
        if(v.varValue > 0):
            print(v.name, "=", v.varValue)
            name = v.name.split('x_')[1].replace("_", " ")
            name = name.split("', '")[1]
            name = name.split("')")[0]
            solution += [name]

    return solution