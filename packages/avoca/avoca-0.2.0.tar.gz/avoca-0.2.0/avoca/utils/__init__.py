import pandas as pd


def compounds_from_df(df: pd.DataFrame) -> list[str]:
    """Get the compounds from a dataframe.

    Args:
        df: The dataframe to get the compounds from.

    Returns:
        The compounds in the dataframe.
    """
    return [c for c in df.columns.get_level_values(0).unique() if c != "-"]


def runtypes_from_df(df: pd.DataFrame) -> list[str]:
    """Get the runtypes from a dataframe.

    Args:
        df: The dataframe to get the runtypes from.

    Returns:
        The runtypes in the dataframe.
    """
    return list(df[("-", "type")].unique())
