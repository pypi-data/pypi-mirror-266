# Create class for the querry points using Gaussian Process, UCB and Set-level filtration
# Each querry point is a connected component of the matrix of points x in the domain adove the level set
# The constrains are mean(x) < CI and (x-mu(x))'cov(x)(x-mu(x)) <= CI^2 if the connected component has more than one point
# D_0: initial database
# x: variables of the data as a list of symbols
# dims: number of dimensions of the variables
# bounds: bounds of the variables as a list
# kernel: kernel of the Gaussian Process

import numpy as np
import sys
from itertools import product, permutations
 
def Slf(mesh, p_mesh, dims, q0, jobs, af_params, constraints_method, sense, model, models_const, Acq_fun):

    def Flatten(l):

        return [item for sublist in l for item in sublist]

    def Filtration(x, score, p_x, dims, level, sense):
        if sense == "maximize":
            data_matrix = np.array([score > level])[0]
        elif sense == "minimize":
            data_matrix = np.array([score < level])[0]
        # Reshape the data
        data_matrix = data_matrix.reshape(*[p_x]*dims)

        return data_matrix.astype(int), x.reshape(*[p_x]*dims, dims)

    def Find_connected_elements(nodes, matrix):
        # Number of dimensions
        D = [nodes.shape[i] for i in range(dims)]
        D0 = D[0]
        # Define the neighbors
        s_neg = [-1]
        s_pos = [1]
        for i in range(dims-1):
            s_neg.append(0)
            s_pos.append(0)
        neigh = tuple(set(permutations(s_neg, dims)) | set(permutations(s_pos, dims)))
            
        def dfs_connected(element, value):
            #
            elem_tuple = tuple(element)
            # Check if the current cell is outside the matrix or has a different value
            if [False for i in range(len(element)) if element[i] < 0] or [False for i in range(len(element)) if element[i] >= D[i]] or nodes[elem_tuple] != value:
                return []
            
            # Mark the cell as visited
            nodes[elem_tuple] = -1
            # Initialize the connected component with the current cell
            nodes_conected = [elem_tuple]
            # Check the neighbors
            for dr in neigh:
                nodes_conected.extend(dfs_connected([element[i] + dr[i] for i in range(len(element))], value))
            
            return nodes_conected
        
        list_connected_components = []
        d = product(range(D0), repeat=dims)
        # 
        for i in d:
            if nodes[i] == 1:
                nodes_conected = dfs_connected(i, nodes[i])
                list_connected_components.append(nodes_conected)
        
        connected_elements = [np.array([matrix[tuple(list_connected_components[k][i])] for i in range(len(list_connected_components[k]))]) for k in range(len(list_connected_components))]
        
        return connected_elements

    def List_of_elements(x, score, p_x, n_elements, dims, q, sense):
        #
        connected_elements = []
        level = np.percentile(np.concatenate(score), q)
        if level == 0:
            level = np.mean(np.concatenate(score))
        #
        for j in range(n_elements):
            x_flitred = Filtration(x[j], score[j], p_x[j], dims, level, sense)
            connected_elements.append(Find_connected_elements(x_flitred[0], x_flitred[1])) 

        connected_elements = [x for x in connected_elements if x != []]
        connected_elements = Flatten(connected_elements)
        n_connected_elements = len(connected_elements)

        return connected_elements, n_connected_elements
    
    def Reduce_num_elements(x, mesh, score, n_elements, jobs, sense):

        def Replace_val(value, arr_1, arr_2):

            return arr_2[(arr_1 == value).all(axis=1)].reshape(-1)

        score_all = np.concatenate(score)
        mesh_all = np.concatenate(mesh)
        scores_lst = []
        scores_mean = []

        for i in range(n_elements):
            #connected_elements[0]
            scores_lst.append(np.array([Replace_val(x[i][j], mesh_all, score_all) for j in range(len(x[i]))]))

        for i in range(n_elements):
            try:
                scores_mean.append(np.mean(scores_lst[i]))
            except:
                sys.exit(1)
                
        if sense == "maximize":
            sorted = np.sort(scores_mean)[::-1][:jobs]
        elif sense == "minimize":
            sorted = np.sort(scores_mean)[:jobs]
        l = np.array([np.where(scores_mean == sorted[i]) for i in range(len(sorted))]).reshape(-1)
        connected_elements = [x[i] for i in l]
        n_connected_elements = len(connected_elements)

        return connected_elements, n_connected_elements
    
    score = [Acq_fun(mesh[i], af_params, constraints_method, model, models_const) for i in range(len(mesh))]
    n_elements = len(mesh)
    q_D = []
    flag = 0
    
    for q in range(q0, 0, -5):
        if sense == "maximize":
            connected_elements, n_connected_elements = List_of_elements(mesh, score, p_mesh, n_elements, dims, q, sense)
            q_D.append([q, connected_elements, n_connected_elements])
        elif sense == "minimize":
            connected_elements, n_connected_elements = List_of_elements(mesh, score, p_mesh, n_elements, dims, 100-q, sense)
            q_D.append([100-q, connected_elements, n_connected_elements])
        if n_connected_elements < jobs:
            flag = 1
            break

    if flag == 0:
        q, connected_elements, n_connected_elements = q_D[0][0], q_D[0][1], q_D[0][2]
        connected_elements, n_connected_elements = Reduce_num_elements(connected_elements, mesh, score, n_connected_elements, jobs, sense)

    return connected_elements, n_connected_elements