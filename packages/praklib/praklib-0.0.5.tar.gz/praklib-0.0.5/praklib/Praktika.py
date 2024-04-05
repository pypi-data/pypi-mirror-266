import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model

def graf_bez_fitu(x, y, errx, erry, xlabel, ylabel, linelabel, scatterlabel,
                grid=True, show=True, scatter=True, line=False, err=True):
    plt.xlim(x[0] - errx[0], x[len(x) - 1] + errx[len(x) - 1])
    data1 = np.arange(x[0] - errx[0], x[len(x) - 1] + errx[len(x) - 1],
                      (x[len(x) - 1] + errx[len(x) - 1] - x[0] - errx[0]) / 100, dtype=np.double)
    if (grid == True):
        plt.grid(True, linestyle="dashed")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if (line == True):
        f, = plt.plot(x, y, linewidth=0.8, c="teal",
                  label=linelabel, marker="none")
    if (scatter == True):
        g = plt.scatter(x, y, s=5, facecolor="red", marker='x', zorder=2, label=scatterlabel)
    if (err == True):
        plt.errorbar(x, y, xerr=errx, yerr=erry, zorder=1, capsize=2, fmt='none',
                 ecolor="red", linewidth=1.0)
    plt.legend()
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

def graf_z_fitu(x, y, fit_vstup, fit_vystup, errx, erry, xlabel, ylabel, linelabel, scatterlabel, params_fit,
                fit_function, grid=True, show=True, scatter=True):
    plt.xlim(x[0]-errx[0], x[-1]+errx[-1])
    data1 = np.linspace(x[0]-errx[0], x[-1]+errx[-1], 100)

    param_names, param_values, param_errors = fit_data(fit_vstup, fit_vystup, params_fit, fit_function, show_results=False)
    funkcni_param = np.array(param_values) + 1j * np.array(param_errors)
    params = dict(zip(param_names, funkcni_param))

    data2 = fit_function(data1, **params)

    if grid:
        plt.grid(True, linestyle="dashed")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.plot(data1, data2.real, linewidth=0.8, c="teal", label=linelabel)
    if scatter:
        plt.scatter(x, y, s=5, facecolor="red", marker='x', zorder=2, label=scatterlabel)
    plt.errorbar(x, y, xerr=errx, yerr=erry, zorder=1, capsize=2, fmt='none',
                 ecolor="red", linewidth=1.0)
    plt.legend()
    plt.show()
