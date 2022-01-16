import numpy as np
from opt.utils_logarithmic_barrier import logarithmic_barrier, \
                                           constraint_inequalities_funcs_eval, \
                                           plot_inner_iterations, \
                                           plot_central_path
from opt.compute_step_size import line_search_for_log_barrier_by_backtracking
from opt.utils import compute_error, print_iterations

def primal_dual_method(f,
                       x_0,
                       t_B,
                       constraints_ineq,
                       mu,
                       x_ast,
                       p_ast,
                       gf_B,
                       Hf_B,
                       plot=True,
                       tol_inner_iter=1e-8,
                       tol_outer_iter=1e-6,
                       tol_backtracking=1e-12,
                       max_inner_iter=30,
                       max_total_iterations=30):
    """
    Outer iterations for logarithmic barrier method
    to numerically approximate solution of PL with only inequalities.

    Args:

        f (fun): definition of original function
            as lambda expression or function definition.

        constraints_ineq: dictionary of inequalities constraints
            in "<= 0" form.

        x_0 (numpy ndarray): initial point for Newton's method.

        tol_inner_iter (float): tolerance that will halt method.
            Controls stopping criteria.

        tol_backtracking (float): tolerance that will halt method.
            Controls value of line search by backtracking.

        t_B (float): parameter barrier.

        plot (bool): if true make plots of Err vs iterations and
            plot of inner iterations.

        x_ast (numpy ndarray): solution of min f_o subject to Ax <= b.
            It's required that user knows the solution...

        p_ast (float): value of f_B(x_ast).

        max_inner_iter (int): maximum number of inner iterations.

        mu (float): parameter that will multiply barrier parameter.

        gf_B (fun): definition of gradient of f_B (logarithmic barrier)
            as lambda expression or function definition.

        Hf_B (fun): definition of Hessian of f_B (logarithmic barrier)
            as lambda expression or function definition.

        tol_outer_iter (float): tolerance that will halt method.
            Controls stopping criteria.

        max_total_iter (int): maximum number of total iterations.

    Returns:

        x (numpy ndarray): numpy array, approximation of x_ast.

        total_iter (int): number of iterations regarding outer and
            inner iterations.

        t_B (float): updated barrier parameter.

        x_plot_total_iter (numpy ndarray): numpy array that containts
            in columns vector of approximations of all inner iterations.
            Last column contains x, approximation of solution. Useful
            for plotting.
    """
    x = x_0
    n = x.size
    log_barrier_eval = logarithmic_barrier(f,x,t_B,constraints_ineq)
    m = len(constraints_ineq.keys())
    stopping_criteria = m/t_B
    outer_iter = 0
    total_iter = 0
    const_funcs_eval = -constraint_inequalities_funcs_eval(x,constraints_ineq)

    if(sum(const_funcs_eval < -np.nextafter(0,1)) >=1):
        print("Some constraint inequalities evaluated in x were nonpositive, change initial point")
    else:
        print("Outer iterations of primal-dual LB method")
        print('{} {:0.2e}'.format("Mu value:", mu))
        columns = ["Outer iter", "logbarrier", "t_log_barrier",
                   "duality gap"]
        list_values = [outer_iter, log_barrier_eval, t_B,
                       stopping_criteria]
        data = {"row" + str(outer_iter): list_values}
        print_iterations(data, columns)
        print("-"*65 + "\n" + "-"*65)
        error_between_iterations = 1

        while(stopping_criteria > tol_outer_iter \
              and error_between_iterations > tol_outer_iter \
              and total_iter < max_total_iterations):
            x_aux = x
            [x,
             inner_iterations,
             Err_plot,
             x_plot] = logarithmic_barrier_newton_method(f,
                                                         constraints_ineq,
                                                         t_B, x, tol_inner_iter,
                                                         tol_backtracking,
                                                         x_ast, p_ast,
                                                         max_inner_iter,
                                                         gf_B,
                                                         Hf_B)
            if(outer_iter == 0):
                x_plot_total_iter = x_plot
            else:
                x_plot_total_iter = np.column_stack((x_plot_total_iter,
                                                     x_plot))
            error_between_iterations = compute_error(x, x_aux)
            if(error_between_iterations > tol_outer_iter):
                if plot:
                    plot_inner_iterations(Err_plot)
                    plot_central_path(x_plot)
                print("Inner iterations")
                print(x)
                const_ineq_funcs_eval = -constraint_inequalities_funcs_eval(x,
                                                                            constraints_ineq)
                t_B=mu*t_B
                log_barrier_eval = logarithmic_barrier(f,x,t_B,
                                                       constraints_ineq)
                if(sum(const_ineq_funcs_eval < -np.nextafter(0,1)) >=1):
                    print("Some constraint inequalities evaluated in x were nonpositive, check approximations")
                    total_iter = max_total_iterations
                    x = t_B = x_plot_total_iter = None
                else:
                    outer_iter+=1
                    stopping_criteria = m/t_B
                    total_iter+= total_iter + inner_iterations
                    #print
                    print("-"*65 + "\n" + "-"*65)
                    print("Outer iterations of primal-dual LB method")
                    print('{} {:0.2e}'.format("Mu value:", mu))
                    list_values = [outer_iter, log_barrier_eval, t_B,
                                   stopping_criteria]
                    data = {"row" + str(outer_iter): list_values}
                    print_iterations(data, columns)
                    print("-"*65 + "\n" + "-"*65)
    return [x,total_iter,t_B,x_plot_total_iter]

def logarithmic_barrier_newton_method(f, constraints_ineq,
                                      t_B, x_0, tol,
                                      tol_backtracking, x_ast=None,
                                      p_ast=None, maxiter=30,
                                      gf=None,
                                      Hf=None):
    """
    Logarithmic barrier primal-dual method using Newton's method
    to numerically approximate solution of PL with only inequalities.

    Args:

        f (fun): definition of objective function
            as lambda expression or function definition.

        constraints_ineq: dictionary of inequalities constraints
            in "<= 0" form.

        t_path: barrier parameter.

        x_0 (numpy ndarray): initial point for Newton's method.

        tol (float): tolerance that will halt method.
            Controls stopping criteria.

        tol_backtracking (float): tolerance that will halt method.
            Controls value of line search by backtracking.

        x_ast (numpy ndarray): solution of min f_o subject to Ax <= b.
            It's required that user knows the solution...

        p_ast (float): value of f_o(x_ast).

        maxiter (int): maximum number of iterations.

        gf (fun): definition of gradient of f as lambda
            expression or function definition.

        Hf (fun): definition of Hessian of f as lambda
            expression or function definition.
    Returns:

        x (numpy ndarray): numpy array, approximation solution of
            inner iterations problem.

        iteration (int): number of iterations.

        Err_plot (numpy ndarray): numpy array of absolute error
            between p_ast and f(x) with x approximation of x_ast.
            Useful for plotting.

        x_plot (numpy ndarray): numpy array that containts in columns
            vector of approximations. Last column contains x, approximation
            of solution. Useful for plotting.
    """
    iteration = 0

    x = x_0
    n = x.size

    #Eval
    f_eval = f(x)
    gf_eval = gf(x, t_B)
    Hf_eval = Hf(x, t_B)

    normgf = np.linalg.norm(gf_eval)
    condHf = np.linalg.cond(Hf_eval)
    Err_plot_aux = np.zeros(maxiter)
    Err_plot_aux[iteration]=compute_error(p_ast,f_eval)

    Err = compute_error(x_ast,x)

    system_matrix = Hf_eval
    rhs = -gf_eval

    x_plot = np.zeros((n,maxiter))
    x_plot[:,iteration] = x

    #Newton's direction and Newton's decrement
    dir_Newton = np.linalg.solve(system_matrix, rhs)
    dec_Newton_squared = rhs.dot(dir_Newton)
    columns = ["Iter", "Normgf_B", "Newtons decrement",
               "Err x ast", "Err p ast",
               "line search", "CondHf_B"]
    list_values = [iteration, normgf, dec_Newton_squared,
                   Err, Err_plot_aux[iteration], "---", condHf]
    data = {"row" + str(iteration): list_values}

    #print
    print_iterations(data, columns)

    #stopping criteria
    stopping_criteria = dec_Newton_squared/2
    iteration+=1

    while(stopping_criteria>tol and iteration < maxiter):
        der_direct = -dec_Newton_squared
        t = line_search_for_log_barrier_by_backtracking(f,dir_Newton,
                                                        x,t_B,
                                                        constraints_ineq,
                                                        der_direct)
        x = x + t*dir_Newton

        #Eval
        f_eval  = f(x)
        gf_eval = gf(x, t_B)
        Hf_eval = Hf(x, t_B)

        system_matrix = Hf_eval
        rhs = -gf_eval

        #Update
        dir_Newton = np.linalg.solve(system_matrix, rhs)
        dec_Newton_squared = rhs.dot(dir_Newton)
        Err_plot_aux[iteration]=compute_error(p_ast,f_eval)
        x_plot[:,iteration] = x
        Err = compute_error(x_ast,x)
        stopping_criteria = dec_Newton_squared/2
        condHf = np.linalg.cond(Hf_eval)
        normgf = np.linalg.norm(gf_eval)

        #print
        list_values = [iteration, normgf, dec_Newton_squared,
                       Err, Err_plot_aux[iteration], t, condHf]
        data = {"row" + str(iteration): list_values}
        print_iterations(data, columns)

        if t<tol_backtracking: #if t is less than tol_backtracking
                               #then we need to check the reason
            iter_salida=iteration
            iteration = maxiter - 1
        iteration+=1
    print('{} {:0.2e}'.format("Error of x with respect to x_ast:",Err))
    print('{} {}'.format("Approximate solution:", x))
    idx_columns_for_plot = Err_plot_aux > np.finfo(float).eps*10**(-2)
    Err_plot = Err_plot_aux[idx_columns_for_plot]

    if iteration == maxiter and t < tol_backtracking:
        print("Backtracking value less than tol_backtracking, check approximation")
        iteration=iter_salida
    else:
        if iteration == maxiter:
            print("Reached maximum of iterations, check approximation")
    x_plot = x_plot[:,:iteration]
    return [x,iteration,Err_plot,x_plot]
