from avoca import io
from avoca.testing.df import simple_df


def test_from_to_csv():
    # Store the dataframe
    io.to_csv(simple_df, "simple_df.csv")
    # Read the dataframe
    df = io.from_csv("simple_df.csv")
    # Check if the dataframes are equal
    assert simple_df.equals(df)
