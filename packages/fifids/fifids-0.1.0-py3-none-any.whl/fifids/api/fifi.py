import polars as pl
import pandas as pd
from .plot import Plot
import matplotlib.pyplot as plt
from .outliers import Outliers
from .pipeline import Pipeline


class Fifi:
    """
    Main class for accessing the library
    """
    def __init__(self, df: pl.DataFrame | pd.DataFrame, target: str = None, time_series: bool = False):
        """Initialize a new instance of the Fifi class.
        @param df: DataFrame to work with.
        @param target: Target column for supervised learning.
        @param time_series: Whether the DataFrame is a time series or not, when this is set to `True`, make sure that the index is a DateTimeIndex.
        """
        self.df = df
        self.target = target
        self.time_series = time_series
        plt.style.use("fivethirtyeight")
        plt.rcParams["figure.figsize"] = 15, 10
        

    def describe(self) -> dict:
        """Generate a report for a DataFrame.
        @param df: DataFrame to generate a report for.
        @return: Dictionary containing the report, iterate over it or use each key as needed.
        """
        print("Types")
        print(self.df.dtypes)
        print("\nShape")
        print(f"Rows: {self.df.shape[0]}")
        print(f"Columns: {self.df.shape[1]}\n") if len(self.df.shape) > 1 else None
        return self.df.describe()

    def plots(self):
        """Create a Plot instance for a DataFrame.
        You can use this to plot different kinds of plots.
        @param df: DataFrame to plot.
        """
        return Plot(self.df, self.target, self.time_series)
    
    def outliers(self):
        """
        Explore and decide how to handle outliers.
        """
        return Outliers(self.df)
    
    def pipeline(self):
        """
        Create a pipeline for the DataFrame.
        """
        return Pipeline(self.df, self.target, self.time_series)

    def __repr__(self):
        methods = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")]
        methods_str = ""
        for method in methods:
            doc = getattr(self, method).__doc__
            methods_str += f"{method}: {doc}\n    "
        return f"Welcome to Fifi!\nPossible methods:\n    {methods_str}"
