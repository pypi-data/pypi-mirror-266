from pathlib import Path

import pandas as pd


def to_csv(df: pd.DataFrame, path: Path):
    """Export a dataframe to a csv file."""
    df.to_csv(path, index=False)


def from_csv(path: Path) -> pd.DataFrame:
    """Read a csv file to a dataframe."""
    return pd.read_csv(path, header=[0, 1])
