"""
You need to crunch through large datasets and generate summaries or
other kinds of statistics.
"""


def example_1():
    """For illustrative purposes only"""
    import pandas as pd

    # Reading csv
    df = pd.read_csv("rats.csv", skipfooter=1)

    # Getting distrinct values fomr a column
    df["Current Activity"].unique()

    # Filtering
    df[df["Current Activity"] == "Dispatch Crew"]

    # Finding top 10 value
    df["ZIP Code"].value_counts().head(10)

    # Group by
    grp = df.groupby("Completion Date")
    sizes = grp.size()
    sizes.sort_values()


def main():
    pass


if __name__ == "__main__":
    main()
