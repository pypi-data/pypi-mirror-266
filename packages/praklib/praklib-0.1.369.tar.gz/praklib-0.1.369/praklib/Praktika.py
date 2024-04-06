import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model
import uncertainties.unumpy as unp


def round_uncertainties(array):
    rounded_values = []
    rounded_errors = []
    for x in array:
        rounded_value, rounded_error = custom_round(x.nominal_value, x.std_dev)
        rounded_values.append(rounded_value)
        rounded_errors.append(rounded_error)
    return unp.uarray(rounded_values, rounded_errors)

def custom_round(value, error):
    # Define a threshold for treating the error as effectively zero
    epsilon = 1e-10

    # Check if the error is effectively zero
    if error < epsilon:
        return 0.0, 0.0

    # Calculate the magnitude of the error
    error_magnitude = int(np.floor(np.log10(error)))

    # Determine the rounding precision based on the first decimal digit of the error
    if error_magnitude < 0:
        rounding_precision = -error_magnitude
    elif error_magnitude == 0:
        if int(error * 10) % 10 == 1:
            rounding_precision = 2
        else:
            rounding_precision = 1
    else:
        rounding_precision = 0

    # Round the value and the error
    rounded_value = round(value, rounding_precision)
    rounded_error = round(error, rounding_precision)

    return rounded_value, rounded_error

def graf(x, y, errx, erry, xlabel, ylabel, linelabel, scatterlabel,
        grid=True, show=True, scatter=True, line=False, err=True, xlim=(0,0), ylim =(0,0), loc="upper right",
        scattercolor="red", linecolor="teal", marker="x"):
    if (xlim == (0,0)):
        plt.xlim(x[0] - errx[0], x[len(x) - 1] + errx[len(x) - 1])
    else:
        plt.xlim(xlim[0], xlim[1])
    if (ylim != (0,0)):
        plt.ylim(ylim[0], ylim[1])
    if (grid == True):
        plt.grid(True, linestyle="dashed")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if (line == True):
        f, = plt.plot(x, y, linewidth=0.8, c=linecolor,
                  label=linelabel, marker="none")
    if (scatter == True):
        g = plt.scatter(x, y, s=5, facecolor=scattercolor, marker=marker, zorder=2, label=scatterlabel)
    if (err == True):
        plt.errorbar(x, y, xerr=errx, yerr=erry, zorder=1, capsize=2, fmt='none',
                 ecolor=scattercolor, linewidth=1.0)
    plt.legend(loc=loc)
    if (show == True):
        plt.show()
def fit_data(y, z, initial_params, fit_function, show_results=True):
    model = Model(fit_function)
    params = model.make_params()
    for param_name in initial_params.keys():
        params.add(param_name, value=initial_params[param_name])
    results = model.fit(z, params, x=y)
    if show_results:
        print(results.fit_report())

    param_names = list(results.params.keys())
    param_values = [results.params[name].value for name in param_names]
    param_errors = [results.params[name].stderr if results.params[name].stderr else 0 for name in param_names]

    return param_names, param_values, param_errors

def graf_fit(x, y, fit_vstup, fit_vystup, errx, erry, xlabel, ylabel, linelabel, scatterlabel, params_fit,
             fit_function, grid=True, show=True, scatter=True, xlim=(0,0), ylim =(0,0), loc="upper right",
             scattercolor="red", linecolor="teal", marker="x"):
    if (xlim == (0, 0)):
        plt.xlim(x[0] - errx[0], x[len(x) - 1] + errx[len(x) - 1])
    else:
        plt.xlim(xlim[0], xlim[1])
    if (ylim != (0,0)):
        plt.ylim(ylim[0], ylim[1])
    data1 = np.linspace(x[0]-errx[0], x[-1]+errx[-1], 500)

    param_names, param_values, param_errors = fit_data(fit_vstup, fit_vystup, params_fit, fit_function, show_results=False)
    funkcni_param = np.array(param_values) + 1j * np.array(param_errors)
    params = dict(zip(param_names, funkcni_param))

    data2 = fit_function(data1, **params)

    if grid:
        plt.grid(True, linestyle="dashed")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.plot(data1, data2.real, linewidth=0.8, c=linecolor, label=linelabel)
    if scatter:
        plt.scatter(x, y, s=5, facecolor=scattercolor, marker=marker, zorder=2, label=scatterlabel)
    plt.errorbar(x, y, xerr=errx, yerr=erry, zorder=1, capsize=2, fmt='none',
                 ecolor=scattercolor, linewidth=1.0)
    plt.legend(loc=loc)
    if show==True:
        plt.show()


def latex_table(data, col_names, err=True):
    num_rows = len(data)
    num_cols = len(data[0])

    latex_table = "\\begin{table}[h!]\n"
    latex_table += "\\centering\n"
    latex_table += "\\begin{tabular}{|" + "|".join(["c"] * (num_cols)) + "|}\n"
    latex_table += "\\hline\n"
    latex_table += " & " + " & ".join(col_names) + " \\\\\n"
    latex_table += "\\hline\n"

    if err==True:
        for i in range(num_rows):
            latex_table += " & " + " & ".join([f"${val[0]} \\pm {val[1]}$" for val in data[i]]) + " \\\\ \\hline \n"
    if err==False:
        for i in range(num_rows):
            latex_table += " & " + " & ".join([f"${val}$" for val in data[i]]) + " \\\\ \\hline \n"

    latex_table += "\\hline\n"
    latex_table += "\\end{tabular}\n"
    latex_table += "\\caption{Values and their errors}\n"
    latex_table += "\\label{tab:values}\n"
    latex_table += "\\end{table}"

    return latex_table

def graf_3d(data, xlabel = "X", ylabel = "Y", zlabel = "Z", cbarlabel = "height", cmap='viridis', projection='ortho', fcl=1):

    # Create meshgrid
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    X, Y = np.meshgrid(x, y)

    # Create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot surface
    ax.plot_surface(X, Y, data, cmap='viridis')

    # Set labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    cbar = fig.colorbar(ax.collections[0], ax=ax, orientation='vertical')
    cbar.set_label(cbarlabel)

    if projection=='ortho':
        ax.set_proj_type(projection)
    else:
        ax.set_proj_type(projection, focal_length=fcl)

    # Show plot
    plt.show()