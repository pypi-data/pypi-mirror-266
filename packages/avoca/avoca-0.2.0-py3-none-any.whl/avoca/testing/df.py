"""Store dataframes for testing purposes."""

import numpy as np
import pandas as pd

simple_df = pd.DataFrame(
    np.ones((2, 4)),
    columns=pd.MultiIndex.from_tuples(
        [
            ("compA", "area"),
            ("compA", "C"),
            ("compB", "area"),
            ("compB", "C"),
        ]
    ),
)
