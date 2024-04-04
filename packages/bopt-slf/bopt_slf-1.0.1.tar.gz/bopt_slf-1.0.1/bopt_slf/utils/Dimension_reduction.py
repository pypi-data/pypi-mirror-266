import pandas as pd
import numpy as np
from prince import PCA, MCA, FAMD
from sklearn.ensemble import ExtraTreesRegressor, ExtraTreesClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# *******************************************************

def Trans_data_to_pandas(data, n_x, dims, problem_type):

    if problem_type == "Mixed":
        cols = np.arange(1,dims+1)
        cols = cols.astype(str)
        data = pd.DataFrame(data, columns=cols)
        data[cols[n_x:]] = data[cols[n_x:]].astype(int)
    else:
        data = pd.DataFrame(data)

    return data

# *******************************************************

def Reduce(data, n_x, dims, problem_type, reducer):
    
    data_pd = Trans_data_to_pandas(data, n_x, dims, problem_type)
    
    return np.array(reducer.transform(data_pd))

# *******************************************************

def Inverse(data, pca_inverse, inverter):

    def Back_projection(data, model):

        predictions = {}
        for col, mod in model.items():
            predictions[col] = mod.predict(data)
        
        return predictions
    
    data = pd.DataFrame(data)
    if pca_inverse == "yes":
        data_reconstructed = inverter.inverse_transform(data)
    elif pca_inverse == "no":
        predictions = Back_projection(data, inverter)
        data_reconstructed = np.vstack(([predictions[i] for i in range(len(inverter))])).T

    return data_reconstructed

# *******************************************************

def Train_reducer(data, n_x, dims, problem_type, n_components, reducer):

    data_pd = Trans_data_to_pandas(data, n_x, dims, problem_type)
    if reducer.__module__ == 'prince.pca':
        reducer_train = PCA()
    elif reducer.__module__ == 'prince.famd':
        reducer_train = FAMD()
    elif reducer.__module__ == 'prince.mca':
        reducer_train = MCA()
    else:
        reducer_train = reducer

    reducer_train.n_components = n_components
    data_red = np.array(reducer_train.fit_transform(data_pd))
    
    return data_red, reducer_train

# *******************************************************

def Train_inverter(data, data_reduced, dims, models):

    for i in range(dims):
        model = models[i]
        model.fit(data_reduced, data[:,i])
        models[i] = model

    return models

# *******************************************************

def Find_reducer(data, n_x, dims, n_components, problem_type):

    def Find_n_components_PCA(x_train, x_test, n, reducer, error_min = 0.5, n_max = 6):

        def Train_Red_comp(x_train, n_trial, reducer):

            reducer.n_components = n_trial
            reducer = reducer.fit(x_train)
            
            return reducer
        
        def Reconstruction_error(x_test, reducer):

            X_test_red = reducer.transform(x_test)
            X_test_reconstructed = reducer.inverse_transform(X_test_red)
            
            return r2_score(x_test, X_test_reconstructed)

        for n in range(1, n_max):
            reducer = Train_Red_comp(x_train, n, reducer)
            error = Reconstruction_error(x_test, reducer)
            if error >= error_min:
                break

        return n
    
    def Find_n_components(data, n, reducer, var_max = 50, n_max = 6):

        def Red(reducer, data, n_trial):

            reducer.n_components = n_trial
            reducer = reducer.fit(data)

            return reducer.cumulative_percentage_of_variance_[-1]
        
        for n in range(1, n_max):
            variance = Red(reducer, data, n)
            if variance >= var_max:
                break

        return n

    # Main program
    if (problem_type == "Continuous") and (n_x < 4):
        reducer = None
        reducer_train = None
        dims_red = dims
    else:
        if problem_type == "Continuous":
            reducer = PCA()
            reducer_search = PCA()
            reducer_train = PCA()
        else:
            if problem_type == "Mixed":
                reducer = FAMD()
                reducer_train = FAMD()
            elif problem_type == "Discrete":
                reducer = MCA()
                reducer_train = MCA()
            else:
                pass

    if n_components is None:
        if reducer is None:
            pass
        else:
            data_pd = Trans_data_to_pandas(data, n_x, dims, problem_type)
            if problem_type == "Continuous":
                x_train, x_test = train_test_split(data_pd)
                dims_red = Find_n_components_PCA(x_train, x_test, dims, reducer_search)
                reducer_train = PCA(n_components=dims_red)
                reducer_train = reducer_train.fit(data_pd)
            else:
                dims_red = Find_n_components(data_pd, dims, reducer_train)
    else:
        dims_red = n_components

    return reducer, reducer_train, dims_red

# *******************************************************

def Find_inverter(data, data_reduced, n_x, n_y, dims, problem_type):

    def Find_best_models(x, z, dims, problem_type, method):

        param_clas = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'bootstrap': [True, False]
        }

        if problem_type == "Discrete" and dims < 5:
            random_search = RandomizedSearchCV(method(), param_distributions=param_clas, n_iter=15, cv=dims)
        elif problem_type == "Mixed" and n_y < 5:
            random_search = RandomizedSearchCV(method(), param_distributions=param_clas, n_iter=15, cv=n_y)
        else:
            random_search = RandomizedSearchCV(method(), param_distributions=param_clas, n_iter=15, cv=5)
        random_search.fit(x, z)
        best_params = random_search.best_params_
        best_model = method(**best_params)
        
        return best_model

    def Train_models(x, z, method):

        models = {}
        for col in z.columns:
            model = Find_best_models(x, z[col], problem_type, dims, method)
            model.warm_start = True
            models[col] = model

        return models
    
    data_pd = Trans_data_to_pandas(data, n_x, dims, problem_type)
    if problem_type == "Discrete":
        model = Train_models(data_reduced, data_pd, ExtraTreesClassifier)
    elif problem_type == "Continuous":
        model = Train_models(data_reduced, data_pd, ExtraTreesRegressor)
    elif problem_type == "Mixed":
        model_1 = Train_models(data_reduced, data_pd.iloc[:,:n_x], ExtraTreesRegressor)
        model_2 = Train_models(data_reduced, data_pd.iloc[:,n_x:], ExtraTreesClassifier)
        model = {**model_1, **model_2}
        model_names = np.arange(len(model))
        model = dict(zip(model_names, list(model.values())))

    return model

# *******************************************************

def Red_bounds(mesh, x_l, x_u, n_x, dims, dims_red, problem_type, reducer):

    if reducer is None:
        x_l_red = x_l
        x_u_red = x_u
    else:
        x_mesh_red = Reduce(mesh, n_x, dims, problem_type, reducer)
        x_l_red = np.array([x_mesh_red[0,i] for i in range(dims_red)])
        x_u_red = np.array([x_mesh_red[-1,i] for i in range(dims_red)])

    return x_l_red, x_u_red