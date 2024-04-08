from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def repr_list_as_pd_dataframe(list_arg: list) -> DataFrame:  # type: ignore
    try:
        import pandas as pd
    except Exception as err:
        raise ModuleNotFoundError("To use this method, please install pandas first") from err
    return pd.DataFrame(list_arg)
