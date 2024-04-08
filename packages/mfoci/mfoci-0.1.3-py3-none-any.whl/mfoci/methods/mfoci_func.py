import pandas as pd

from mfoci.methods.multivar_chatterjee import xi_q_n_calculate


def mfoci(factors, response_vars, report_insignificant=False):
    """
    Multivariate FOCI - implements slide 31 from Jonathan's presentation

    :param factors: pd.DataFrame
    :param response_vars: pd.DataFrame

    :return: list
    """
    q = response_vars.shape[1]
    p = factors.shape[1]
    selected_factors = []
    max_t = 0
    max_ts = []
    n_selected = 0
    for i in range(p):
        t_js = []
        for j in range(p):
            if j in selected_factors:
                t_js.append(0)
                continue
            t_ks = []
            k_range = range(q)
            for k in k_range:  # shuffle y order to see effect on T^q
                shuffled_y = pd.concat(
                    [response_vars.iloc[:, k:], response_vars.iloc[:, :k]], axis=1
                )
                t_k = xi_q_n_calculate(
                    factors.iloc[:, selected_factors + [j]], shuffled_y
                )
                t_ks.append(t_k)
            t_j = sum(t_ks) / len(k_range)  # average over different orders of y
            t_js.append(t_j)
        if max(t_js) <= max_t and n_selected == 0:
            n_selected = i
            if not report_insignificant:
                break
        max_t = max(t_js)
        argmax = t_js.index(max_t)
        selected_factors.append(argmax)
        max_ts.append(max_t)

    t = [str(round(i, 3)) for i in max_ts]
    print("\nMFOCI results:")
    ind_str = ", ".join(factors.columns[selected_factors])
    print(f"Predictive indicators are (in this order) {ind_str}")
    print(f"The corresponding T's are {' '.join(t)}")
    print(f"Number of selected variables is {n_selected}.")
    print("Done!")

    return selected_factors, max_ts
