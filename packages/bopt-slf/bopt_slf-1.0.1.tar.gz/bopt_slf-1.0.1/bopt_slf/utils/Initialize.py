# *******************************************************
# Import libraries

import numpy as np
from scipy.stats import qmc
from sklearn.preprocessing import OrdinalEncoder
import time

def Space(domain):

    """ 
    Gets an array for the lower and upper bounds of the continuous variables, and a tuple for the discrete variables.
    """

    dims = len(domain)
    n_x = 0
    n_d = 0
    n_c = 0
    x_l = []
    x_u = []
    dis_val = []
    cat_val = []
    enc_cat = []
    names = []

    for i in range(dims):
        try:
            names.append(domain[i]['name'])
        except:
            names = 0
        if domain[i]['type'] == "continuous":
            n_x += 1
            x_l.append(domain[i]['domain'][0])
            x_u.append(domain[i]['domain'][1])
        elif domain[i]['type'] == "discrete":
            n_d += 1
            dis_val.append(domain[i]['domain'])
        elif domain[i]['type'] == "categorical":
            n_c += 1
            enc_cat.append(OrdinalEncoder())
            X = domain[i]['domain']
            X = [[(X[i])] for i in range(len(X))]
            X_trans = tuple(enc_cat[n_c-1].fit_transform(X).reshape(-1).astype(int))
            cat_val.append(X_trans)
        else:
            pass
            
    x_l, x_u = np.array(x_l), np.array(x_u)
    n_y = n_d + n_c
    y_v = [item for sublist in [dis_val, cat_val] for item in sublist]
    if n_d == 0:
        dis_val = 0
    if n_c == 0:
        enc_cat = None
        cat_val = 0
    if names == 0:
        names = None

    return dims, n_x, n_d, n_c, n_y, x_l, x_u, y_v, dis_val, cat_val, enc_cat, names

# *******************************************************

def Problem_type(n_x, n_y):

    """ 
    Returns the type of problem depending of the characteristics of the inputs:
    * Continuous if there are only continuous variables
    * Discrete if there are only discrete variables
    * Mixed if there are continuous and discrete variables
    """
    
    if n_x > 0 and n_y == 0:
        problem_type = "Continuous"
    elif n_y > 0 and n_x == 0:
        problem_type = "Discrete"
    elif n_x > 0 and n_y > 0:
        problem_type = "Mixed"
    else:
        pass

    return problem_type

# *******************************************************

def Get_constraints(constraints, constraints_method):

    "Transforms tuple of constraints into list"

    n_const = len(constraints)

    if constraints_method == "PoF":
        symbols = ['<=', '>=']
        const = []
        for i in range(n_const):
            for s in symbols:
                try:
                    index_const = constraints[i]['constraint'].index(s)
                    const.append(constraints[i]['constraint'][:index_const-1])
                except:
                    pass
    elif constraints_method == "GPC":
        const = constraints
    
    return const, n_const

# *******************************************************

def Times_fun(fun, x):

    """ 
    Generates the number of points of the mesh or grid, depending on the cost of the evaluation of the function, and the dimensions of the problem
    """
    
    #x = np.zeros(dims)
    start = time.time()
    f_eval = fun(x.reshape(1,-1))
    end = time.time()
    
    return (end - start), f_eval

# *******************************************************

def Points_initial_design(times, dims, design):

    if times <= 1:
        exp_param = 0.25
    else: 
        exp_param = 0.95
    
    c_param = 50
    points_D = int(c_param - c_param/(1+(1/times)**exp_param))

    if design == "Mesh":
        points_D = int(np.ceil(points_D)**(1/dims))
    elif design == "Sobol":
        points = int(np.ceil(np.sqrt(points))**2)
    else:
        pass

    if points_D < 3:
        points_D = int(3)

    return points_D

# *******************************************************

def x_Generator(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type, design_type):

    def Random_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type):

        def X_rand(x_l, x_u, dims, points):

            return np.random.uniform(x_l, x_u, size=(points, dims))
        
        def Y_rand(y_v, n_y, points):

            size_y = [len(y_v[i]) for i in range(n_y)]
            l = [np.repeat(1/size_y[i], size_y[i]) for i in range(n_y)]
            sample = [np.random.choice(y_v[i], p=l[i], size=(points, 1)).reshape(-1) for i in range(n_y)]
            
            return np.array(sample).T

        if problem_type == "Continuous":
            variables = X_rand(x_l, x_u, dims, points)
        elif problem_type == "Mixed":
            x_variables = X_rand(x_l, x_u, n_x, points)
            y_variables = Y_rand(y_v, n_y, points)
            variables = np.hstack((x_variables, y_variables))
        elif problem_type == "Discrete":
            variables = Y_rand(y_v, dims, points)[0]
        else:
            pass

        return variables
    
    def Mesh_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type):

        def X_mesh(lower_bound, upper_bound, dims, points):

            lists = [np.linspace(lower_bound[i], upper_bound[i], points) for i in range(dims)]
            mesh = np.meshgrid(*lists)
            
            return np.array(mesh).T.reshape(-1, dims)
        
        def Bounds_y(n_y):

            y_l = np.zeros(n_y)
            y_u = np.ones(n_y)
            
            return y_l, y_u

        def Assign_y(y_v, n_y, y_norm, points):

                size_y = [len(y_v[i]) for i in range(n_y)]
                l = [[i/size_y[j] for i in range(size_y[j]+1)] for j in range(n_y)]
                for i in range(len(l)):
                    l[i][-1] = l[i][-1] + 0.0001
                y_new = np.empty([points, n_y])

                for i in range(n_y):
                    for j in range(len(y_norm[:,i])):
                        for k in range(len(l[i])-1):
                            if l[i][k] <= y_norm[j,i] < l[i][k+1]:
                                y_new[j,i] = y_v[i][k]
                                break
                
                return y_new

        if problem_type == "Continuous":
            variables = X_mesh(x_l, x_u, dims, points)
        elif problem_type == "Mixed":
            y_l, y_u = Bounds_y(n_y)
            all_vars = X_mesh(np.append(x_l, y_l), np.append(x_u, y_u), dims, points)
            x_variables = all_vars[:, :n_x]
            y_norm = all_vars[:, n_x:]
            y_variables = Assign_y(y_v, n_y, y_norm, y_norm.shape[0])
            variables = np.hstack((x_variables, y_variables))
        elif problem_type == "Discrete":
            y_l, y_u = Bounds_y(n_y)
            y_norm = X_mesh(y_l, y_u, n_y, points)
            variables = Assign_y(y_v, n_y, y_norm, y_norm.shape[0])
        else:
            pass

        return variables
    
    def QMC_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type, design_type):

        def Bounds_y(y_v, n_y):

            y_l = []
            y_u = []
            flag = int(all([(np.diff(y_v[i]) == 1).all() for i in range(n_y)]))
            
            for i in range(n_y):
                if flag == 1:
                    y_l.append(y_v[i][0])
                    y_u.append(y_v[i][-1])
                elif flag == 0:
                    y_l.append(0)
                    y_u.append(1)
                else:
                    pass
            return y_l, y_u, flag

        def X_qmc(x_l, x_u, points, method):
                    
            sample = method.random(n=points)

            return qmc.scale(sample, x_l, x_u)

        def Y_qmc(y_v, n_y, points, method):

            def Assign_y(y_v, n_y, y_norm, points):

                size_y = [len(y_v[i]) for i in range(n_y)]
                l = [[i/size_y[j] for i in range(size_y[j]+1)] for j in range(n_y)]
                for i in range(len(l)):
                    l[i][-1] = l[i][-1] + 0.0001
                y_new = np.empty([points, n_y])

                for i in range(n_y):
                    for j in range(len(y_norm[:,i])):
                        for k in range(len(l[i])-1):
                            if l[i][k] <= y_norm[j,i] < l[i][k+1]:
                                y_new[j,i] = y_v[i][k]
                                break
                
                return y_new
            
            y_l, y_u, flag = Bounds_y(y_v, n_y)
            if flag == 1:
                y_qmc = method.integers(l_bounds=y_l, u_bounds=y_u, n=points, endpoint=True)
            elif flag == 0:
                y_norm = X_qmc(y_l, y_u, points, method)
                y_qmc = Assign_y(y_v, n_y, y_norm, points)        

            return y_qmc

        def Select_method(design_type, dims):
            
            if design_type == "LHS":
                method = qmc.LatinHypercube(d=dims)
            elif design_type == "Sobol":
                method = qmc.Sobol(d=dims)
            elif design_type == "Halton":
                method = qmc.Halton(d=dims)
            else:
                pass

            return method

        if problem_type == "Continuous":
            method = Select_method(design_type, dims)
            variables = X_qmc(x_l, x_u, points, method)
        elif problem_type == "Mixed":
            method = Select_method(design_type, n_x)
            x_variables = X_qmc(x_l, x_u, points, method)
            method = Select_method(design_type, n_y)
            y_variables = Y_qmc(y_v, n_y, points, method)
            variables = np.hstack((x_variables, y_variables))
        elif problem_type == "Discrete":
            method = Select_method(design_type, n_y)
            variables = Y_qmc(y_v, n_y, points, method)
        else:
            pass

        return variables
    
    # Main program
    if design_type == "random":
        variables = Random_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type)
    elif design_type == "LHS":
        variables = QMC_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type, "LHS")
    elif design_type == "Sobol":
        points = int(np.ceil(np.sqrt(points))**2)
        variables = QMC_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type, "Sobol")
    elif design_type == "Halton":
        variables = QMC_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type, "Halton")
    elif design_type == "Mesh":
        variables = Mesh_design(x_l, x_u, y_v, n_x, n_y, dims, points, problem_type)
    else:
        pass
    
    return variables

# *******************************************************

def Bounds(x_l, x_u, dims):

    bnds = np.sort(np.array([[x_l[i], x_u[i]] for i in range(dims)]))
    return tuple(map(tuple, bnds))

# *******************************************************

def Points_mesh(dims, r1=9):

    """ 
    Generates the points mesh
    """
    points = int(np.ceil(2**r1)**(1/dims))

    if points < 3:
        points = 3

    return points

# *******************************************************

def AF_params(z, xi, xi_decay, iters, AF_name, sense):

    if xi_decay == "yes":
        xi_decay = (1/xi)**(1/iters)
    elif xi_decay == "no":
        xi_decay = 1
    else:
        pass

    if sense == "maximize":
        f_best = np.max(z)
    elif sense == "minimize":
        f_best = np.min(z)
    else:
        pass

    return {'xi': xi, 'xi_decay': xi_decay, 'f_best': f_best, 'AF_name': AF_name}