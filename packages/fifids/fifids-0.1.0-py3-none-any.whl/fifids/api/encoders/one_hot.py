import polars as pl
import pandas as pd
import polars.selectors as cs


class OneHotEncoder:
    def __init__(self, df: pl.DataFrame | pd.DataFrame):
        self.df = df
    
    def encode(self) -> pl.DataFrame | pd.DataFrame:
        if isinstance(self.df, pd.DataFrame):
            return pd.get_dummies(self.df.select_dtypes(include='object'))
        return self.df.to_dummies(cs.string())