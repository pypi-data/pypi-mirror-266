import GPy
import numpy as np
import properscoring as ps
from sklearn.model_selection import train_test_split
from sklearn.mixture import GaussianMixture

# *******************************************************

def Select_model(x, z, kernel, surrogate):

    if surrogate == "GP":
        model = GPy.models.GPRegression(x, z, kernel)
    elif surrogate == "SGP":
        model = GPy.models.SparseGPRegression(x, z, kernel)
    else:
        raise ValueError('Not valid surrogate model')
    
    return model

# *******************************************************

def Train_model(model, n_restarts):

    model.optimize(optimizer='lbfgsb', max_iters=1000, messages=False)
    model.optimize_restarts(num_restarts=n_restarts, verbose=False)

    return model

# *******************************************************

def Train_models_const(x, g, n_const, constraints_method):

    def Train_PoF(x, g, n_const):
        
        models = []
        for i in range(n_const):
            model = GPy.models.GPRegression(x, g[:,i].reshape(-1,1))
            model.optimize()
            models.append(model)

        return models
    
    def Train_GPC(x, g):

        y = (g == True).all(axis=1)
        y = y.astype(int)
        model = GPy.models.GPClassification(x, y.reshape(-1,1))
        model.optimize()

        return model
    
    if constraints_method == "PoF":
        models_const = Train_PoF(x, g, n_const)
    elif constraints_method == "GPC":
        models_const = Train_GPC(x, g)
    else:
        pass

    return models_const

# *******************************************************

def Kernel_ABCD(x, z, dims, surrogate, evals, err_min = 0.25):

    def Search(x, z,  kernels):

        # Train the model with the base kernels
        ll, k, models = [], [], {}
        for name, kernel in kernels.items():
            model = Select_model(x, z, kernel, surrogate)
            model.optimize()
            ll.append(model.log_likelihood())
            k.append(model._size_transformed())
            models[name] = model

        return ll, k, x.shape[0], models

    def Bic(ll, k, n): return -2*ll + k*np.log(n)

    def Sort_bic(ll, k, n, models):

        BICs = []
        d = len(models)
        for i in range(d):
            BICs.append(Bic(ll[i], k[i], n))
        
        ordered = [x for _, x in sorted(zip(BICs, models.keys()))]

        return {ordered[0]: models[ordered[0]]}

    x_train, x_test, z_train, z_test = train_test_split(x, z, test_size=0.2)
    # Base kernels: SE, Periodic, Linear, RatQuad  
    kernels = {"linear": GPy.kern.Linear(input_dim=dims),
                    "RBF": GPy.kern.RBF(input_dim=dims, variance=1.0, lengthscale=1.0),
                    "Mater_32": GPy.kern.Matern32(input_dim=dims, variance=1.0, lengthscale=1.0),
                    "Mater_52": GPy.kern.Matern52(input_dim=dims, variance=1.0, lengthscale=1.0),
                    "Periodic": GPy.kern.StdPeriodic(input_dim=dims, variance=1.0, lengthscale=1.0, period=1.0)
                    }

    for _ in range(evals):

        base_kernels = kernels.copy()
        ll, k, n, models = Search(x_train, z_train, base_kernels)
        best_model = Sort_bic(ll, k, n, models)
        base_model = list(best_model.values())[0]
        mean, var = base_model.predict(x_test)
        error = ps.crps_gaussian(z_test, mean, var).mean()
        # Composing best model with base kernels using addition and multiplication
        kernels = {}
        base_model_name = list(best_model.keys())[0]
        base_model_kern = base_model.kern

        for name, kernel in base_kernels.items():
            kernels[base_model_name + "+" + name] = GPy.kern.Add([base_model_kern, kernel])
            kernels[base_model_name + "*" + name] = GPy.kern.Prod([base_model_kern, kernel])

        if error < err_min:
            break

    return base_model