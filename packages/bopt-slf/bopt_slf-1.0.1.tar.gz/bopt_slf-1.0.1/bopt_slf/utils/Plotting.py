import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from ..utils.Acq_fun import AF

def Data_plot(x_l, x_u, dims, n_plot):

    lists = [np.linspace(x_l[i], x_u[i], n_plot) for i in range(dims)]
    # Create a meshgrid data
    x_plot = np.meshgrid(*lists)
    x_plot = np.array(x_plot).T.reshape(-1, dims)
    
    return x_plot

def Plot_fun_1D(x_plot, z_plot):

    plt.plot(x_plot, z_plot)
    plt.xlabel('$x$')
    plt.ylabel('$f(x)$')
    plt.title('function')
    plt.show()

def Plot_fun_2D(x_plot, z_plot, n_plot):
    
    x1_plot, x2_plot = x_plot[:,0].reshape(n_plot, n_plot), x_plot[:,1].reshape(n_plot, n_plot)
    plt.contourf(x1_plot, x2_plot, z_plot, cmap='jet')
    plt.xlabel('$x_1$')
    plt.ylabel('$x_2$')
    plt.title('function')
    cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='jet'))
    plt.show()

def Plot_surrogate(args):

    _, f_best, x_init, f_init, x_iters, f_iters, x_l, x_u, dims, _, _, xi, acquisition_function, _, _, _, model = args.__dict__.values()
    #x_best, f_best, x_init, f_init, x_iters, f_iters, x_l, x_u, dims, iters, inital_design, xi, acquisition_function, regret, constraint_method, models_const, model = args.__dict__.values()

    if dims == 1:
        
        af_params = {'xi': xi, 'xi_decay': None, 'f_best': f_best, 'AF_name': acquisition_function}
        fig = plt.figure()
        n_plot = 500
        x_plot = Data_plot(x_l, x_u, dims, n_plot)
        f_mean, f_std = model.predict(x_plot)

        plt.plot(x_plot, f_mean)
        plt.fill_between(x_plot.reshape(-1), (f_mean - f_std).reshape(-1), (f_mean + f_std).reshape(-1), alpha=0.2)
        plt.scatter(x_init, f_init, c='k', s=10, label='Training data')
        plt.scatter(x_iters, f_iters, c='r', s=10, label='Observations')
        plt.xlabel('$x$')
        plt.ylabel('$f(x)$')
        plt.title('Surrogate model')
        plt.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)
        
    elif dims == 2:

        af_params = {'xi': xi, 'xi_decay': None, 'f_best': f_best, 'AF_name': acquisition_function}
        fig = plt.figure()
        n_plot = 100
        x_plot = Data_plot(x_l, x_u, dims, n_plot)
        f_mean, f_std = model.predict(x_plot)
        x1_plot, x2_plot = x_plot[:,0].reshape(n_plot, n_plot), x_plot[:,1].reshape(n_plot, n_plot)

        plt.contourf(x1_plot, x2_plot, f_mean, cmap='jet')
        #plt.scatter(x[:,0], x[:,1], c='k', s=10, label='Training data')
        plt.set_xlabel('$x_1$')
        plt.set_ylabel('$x_2$')
        plt.set_title('Acquisition function')
        #cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='jet'), ax=ax[1])

        plt.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)

    elif dims > 2:

        print('not posible to plot')
        fig = None

    return fig

def Plot_AF(args):

    _, f_best, _, _, _, _, x_l, x_u, dims, _, _, xi, acquisition_function, _, constraints_method, models_const, model = args.__dict__.values()

    if dims == 1:
        
        af_params = {'xi': xi, 'xi_decay': None, 'f_best': f_best, 'AF_name': acquisition_function}
        fig = plt.figure()
        n_plot = 500
        x_plot = Data_plot(x_l, x_u, dims, n_plot)
        z_acq = AF(x_plot, af_params, constraints_method, model, models_const)

        plt.plot(x_plot, z_acq)
        plt.xlabel('$x$')
        plt.ylabel('$AF(x)$')
        plt.title('Acquisition function')
        
    elif dims == 2:

        af_params = {'xi': xi, 'xi_decay': None, 'f_best': f_best, 'AF_name': acquisition_function}
        fig = plt.figure()
        n_plot = 100
        x_plot = Data_plot(x_l, x_u, dims, n_plot)
        z_acq, _ = AF(x_plot, af_params, constraints_method, model, models_const)
        x1_plot, x2_plot = x_plot[:,0].reshape(n_plot, n_plot), x_plot[:,1].reshape(n_plot, n_plot)
        z_acq = z_acq.reshape(n_plot, n_plot)        

        plt.contourf(x1_plot, x2_plot, z_acq, cmap='jet')
        #plt.scatter(x[:,0], x[:,1], c='k', s=10, label='Training data')
        plt.set_xlabel('$x_1$')
        plt.set_ylabel('$x_2$')
        plt.set_title('Acquisition function')
        #cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='jet'), ax=ax[1])

        plt.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)

    elif dims > 2:

        print('not posible to plot')
        fig = None

    return fig

def Plot_regret(args):

    _, _, _, _, _, _, _, _, dims, _, _, _, _, regret, _, _, _ = args.__dict__.values()
    R = np.cumsum(regret)

    fig = plt.figure()

    plt.plot(regret, label="instantaneous regret")
    plt.plot(R, label="cummulative regret")
    plt.xlabel('Iterations')
    plt.ylabel('R')
    plt.title('Regret')
    plt.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)

    return fig