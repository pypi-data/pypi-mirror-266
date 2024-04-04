from types import SimpleNamespace
import multiprocess as mp
import numpy as np

# *******************************************************

def Errors(n_x, n_y, design_type, surrogate, constraints_method, AF_name):

    valid_var_type = ["continuous", "discrete", "categorical"]
    valid_design_type = ["random", "LHS", "Sobol", "Halton", "Mesh"]
    valid_surrogate_name = ["GP", "SGP"]
    valid_constraints_method = ["PoF", "GPC"]
    valid_af_names = ['UCB', 'EI', 'PI']

    if n_x <= 0 and n_y <= 0:
        raise ValueError("Not valid variable type, valid names are:", *valid_var_type)

    if design_type not in valid_design_type:
        raise ValueError("Not valid design type, valid names are:", *valid_design_type)
    
    if surrogate not in valid_surrogate_name:
        raise ValueError("Not valid acquisition function name, valid names are:", *valid_surrogate_name)
    
    if constraints_method not in valid_constraints_method:
        raise ValueError("Not valid method for constraints, valid names are:", *valid_constraints_method)

    if AF_name not in valid_af_names:
        raise ValueError("Not valid acquisition function name, valid names are:", *valid_af_names)
    
    return None

# *******************************************************

def Data_eval(x, n_c, dims, enc_cat):

    if enc_cat != None:
        x_conv = []
        for i in range(len(enc_cat)):
            ix_cat = (dims - n_c)
            x_conv.append(enc_cat[i].inverse_transform(x[:,ix_cat+i].reshape(-1,1)))
        x_conv = np.array(x_conv).reshape(-1,1)
        x_eval = np.hstack((x[:, :ix_cat], np.asarray(x_conv,object)))
    else:
        x_eval = x
    
    return x_eval

# *******************************************************

def Eval_fun(x, n_elements, parallelization, jobs, function):

    if parallelization == "no":
        x_new = np.array(x).reshape(1,-1)
        z_new = function(x_new)
    elif parallelization == "yes":
        x_new = [x[i].reshape(1,-1) for i in range(n_elements)]
        with mp.Pool(jobs) as pool:
            z_new = pool.map(function, x_new)
        
    return z_new

# *******************************************************

def Eval_const(x, const, n_const, constraints_method):
    
    if constraints_method == "PoF":
        data = [eval(const[i], None, {"x": x}) for i in range(n_const)]
    elif constraints_method == "GPC":
        data = [eval(const[i]['constraint'], None, {"x": x}) for i in range(n_const)]

    return np.array(data).reshape(-1, n_const)

# *******************************************************

def Regret(z_true, x, n_elements, model):
    # Return an average of the reward
    z_pred, _ = model.predict(x)
    rt = [(z_true[i] - z_pred[i]) for i in range(n_elements)]
    rt = sum(rt)

    return rt/n_elements

# *******************************************************

def Print_results(x, enc_cat):

    if enc_cat is None:
        x = x.reshape(-1)
        x_print = ["%.5f" % value if 1e-3 < abs(value) < 1e3 else "%0.1e" % value for value in x]
    else:
        x = x[0]
        x_print = [] 
        for value in x:
            if type(value) == str:
                x_print.append(value)
            elif type(value) == float:
                if 1e-3 < abs(value) < 1e3:
                    x_print.append("%.5f" % value)
                else:
                    x_print.append("%0.1e" % value)
        
    return x_print

# *******************************************************

def Create_results(x_best, z_best, x, z, x_l, x_u, dims, max_iter, points, design, af_params, constraints_method, rt, models_const, model):

    res = {'x_best': x_best, 'f_best': z_best, 
           'x_init': x[0:points], 'f_init': z[0:points], 
           'x_iters': x[points:-1], 'f_iters': z[points:-1],
           'x_l': x_l, 'x_u': x_u, 
           'dims': dims,
           'iters': max_iter, 
           'inital_design': design, 
           'xi': af_params['xi'], 
           'acquisition_function': af_params['AF_name'],
           'regret': rt,
           'constraint_method': constraints_method,
           'models_constraints': models_const,
           'model': model}
    
    return SimpleNamespace(**res)