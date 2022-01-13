import numpy as np
import matplotlib.pyplot as plt

def log_barrier_aux_eval_constraints(eval_f_const_inequality):
    """
    Auxiliary function for evaluation of constraint inequalities
    in logarithmic barrier
    """
    #get values that are nonnegative through indexes
    idx_zeros = np.logical_and(eval_f_const_inequality < np.nextafter(0,1),
                               eval_f_const_inequality > -np.nextafter(0,1))
    idx_negative = eval_f_const_inequality < 0
    idx  = np.logical_or(idx_zeros, idx_negative)
    #eval constraint inequality functions
    #next line produces warning if a value of constraint
    #is nonpositive
    eval_f_const_inequality = np.log(eval_f_const_inequality)
    #assign large negative value for constraints
    #that have values negative or equal to 0
    eval_f_const_inequality[idx] = -1e10
    return eval_f_const_inequality
def constraint_inequalities_funcs_generator(constraint_inequalities):
    """
    Generator for functional form of inequalities.
    For every example this function produces different functions.
    """
    for k, v in constraint_inequalities.items():
        yield v
def constraint_inequalities_funcs_eval(x,
                                       constraint_inequalities):
    """
    Auxiliary function for the evaluation of constraint inequalities
    in logarithmic barrier function
    """
    const_ineq_funcs_eval = np.array([const(x) for const in \
                                      constraint_inequalities_funcs_generator(constraint_inequalities)])
    return const_ineq_funcs_eval
def phi(x, constraint_inequalities):
    """
    Implementation of phi function for logarithmic barrier.
    """
    constraint_ineq_funcs_eval = -constraint_inequalities_funcs_eval(x,constraint_inequalities)
    log_barrier_const_eval = log_barrier_aux_eval_constraints(constraint_ineq_funcs_eval)
    return -np.sum(log_barrier_const_eval)

def logarithmic_barrier(f,x, t_B, constraint_inequalities):
    """
    Implementation of Logarithmic barrier function.
    """
    return t_B*f(x)+ phi(x, constraint_inequalities)
def plot_inner_iterations(err):
    """
    Auxiliary function for plotting inner iterations error.
    """
    plt.yscale('log') #logarithmic scale for y axis
    plt.plot(np.arange(err.size),err,'.-')
    plt.ylabel("Log relative error: $f_o(x^k)$ y $p^*$",size=12)
    plt.xlabel("Inner iterations",size=12)
    plt.grid()
    plt.show()
def plot_central_path(x_iterations):
    """
    Auxiliary function for plotting central points of
    central path.
    """
    plt.plot(x_iterations[0,:],
             x_iterations[1, :], "-*")
    plt.ylabel("$x_2$")
    plt.xlabel("$x_1$")
    plt.annotate("$x^{(0)}$",(x_iterations[0,0],
                              x_iterations[1,0]),fontsize=12)
    plt.title("Primal-dual BL method iterations")
    plt.grid()
    plt.legend(["Trayectoria central"], bbox_to_anchor=(1,1))
    plt.show()
