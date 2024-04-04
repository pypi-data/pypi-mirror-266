import numpy as np

def Up_mesh(mesh, n_mesh, p_mesh, dims):

    def New_boundaries(mesh, n_mesh, dims):

        x_l_new, x_u_new = [], []

        for i in range(n_mesh):
            x_l_new.append([np.min(mesh[i][:,j]) for j in range(dims)])
            x_u_new.append([np.max(mesh[i][:,j]) for j in range(dims)])
        
        return x_l_new, x_u_new
    
    def Points_mesh(x_l, x_u, points_mesh, n_mesh, dims):

        l = [[(x_u[i][j] - x_l[i][j]) for i in range(n_mesh)] for j in range(dims)]
        a = [np.prod(l[0][i]) for i in range(n_mesh)]
        pts = a/np.max(a)
        points_mesh_min = int(np.sqrt(points_mesh))

        return [points_mesh_min if int(x*points_mesh) < points_mesh_min else int(x*points_mesh) for x in pts]

    x_l_new, x_u_new = New_boundaries(mesh, n_mesh, dims)
    points_mesh_new = Points_mesh(x_l_new, x_u_new, p_mesh, n_mesh, dims)
    x_mesh_new = []

    for i in range(n_mesh):
        lists = [np.linspace(x_l_new[i][j], x_u_new[i][j], points_mesh_new[i]) for j in range(dims)]
        x_mesh_new.append(np.meshgrid(*lists))
        x_mesh_new[i] = np.array(x_mesh_new[i]).T.reshape(-1, dims)

    return x_mesh_new, points_mesh_new