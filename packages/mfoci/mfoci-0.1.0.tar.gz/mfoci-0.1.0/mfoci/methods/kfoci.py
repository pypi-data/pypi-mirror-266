import pathlib
import subprocess

import pandas as pd


def kfoci(factors, response_vars, r_path):
    """
    Kernel FOCI - implements slide 31 from Jonathan's presentation

    :param factors: pd.DataFrame
    :param response_vars: pd.DataFrame

    :return: list
    """
    # start r subprocess calling
    factors.to_csv("x.csv", index=False)
    response_vars.to_csv("y.csv", index=False)
    path = pathlib.Path(__file__).parent
    filename = str(path / "kfoci.R")
    cmd_list = [r_path, "--vanilla", filename, path]
    subprocess.call(cmd_list, shell=True)
    selected_cols_df = pd.read_csv(f"{path}/selected_cols_linear.csv")
    selected_cols_linear = selected_cols_df.iloc[:, 0].tolist()
    selected_cols_df = pd.read_csv(f"{path}/selected_cols_gaussian.csv")
    selected_cols_gaussian = selected_cols_df.iloc[:, 0].tolist()
    print("KFOCI rbfdot selected indicators:")
    print(selected_cols_linear)
    print("KFOCI linear selected indicators:")
    print(selected_cols_gaussian)
    return selected_cols_linear, selected_cols_gaussian
