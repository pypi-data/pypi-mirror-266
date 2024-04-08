from mfoci.methods.mfoci_func import mfoci
from mfoci.methods.kfoci import kfoci
from mfoci.methods.lasso import select_indicators_with_lasso


def select_factors(factors, response_vars, method="mfoci", **kwargs):
    """
    Select factors using a specified method

    :param factors: pd.DataFrame
    :param response_vars: pd.DataFrame
    :param method: str

    :return: list
    """
    if method == "mfoci":
        return mfoci(factors, response_vars)
    elif method == "kfoci":
        if "r_path" not in kwargs:
            raise ValueError(
                "R path must be specified for kfoci method, "
                "e.g. 'C:/Program Files/R/R-4.3.3/bin/x64/Rscript'."
            )
        return kfoci(factors, response_vars, kwargs["r_path"])
    elif method == "lasso":
        return select_indicators_with_lasso(factors, response_vars)
    else:
        raise ValueError(f"Method {method} not implemented.")
