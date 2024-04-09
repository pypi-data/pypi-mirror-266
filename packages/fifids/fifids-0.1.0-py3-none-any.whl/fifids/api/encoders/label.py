import polars as pl
import polars.selectors as cs
from sklearn.preprocessing import LabelEncoder as LE
import pandas as pd


class LabelEncoder:
    def __init__(self, df: pl.DataFrame | pd.DataFrame):
        self.df = df
    
    def encode(self) -> pl.DataFrame | pd.DataFrame:
        label_encoder = LE()
        if isinstance(self.df, pd.DataFrame):
            for col in self.df.select_dtypes(include='object').columns:
                self.df[col] = label_encoder.fit_transform(self.df[col])
        else:
            for col in self.df.select(cs.string()).columns:
                self.df.replace(col, pl.Series(label_encoder.fit_transform(self.df[col])))
        
        return self.df
        
    
    