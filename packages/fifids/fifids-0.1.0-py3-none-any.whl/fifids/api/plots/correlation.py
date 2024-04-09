import seaborn as sns
import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fifi.api.encoders.one_hot import OneHotEncoder
from fifi.api.encoders.label import LabelEncoder
from typing import Literal


class Correlation:
    def __init__(self, df: pl.DataFrame | pd.DataFrame, method:Literal['pearson', 'spearman'] = 'pearson', encoder:Literal['label', 'one_hot'] = 'label'):
        self.df = df
        self.method = method
        self.encoder = encoder
    
    def show(self):
        df = LabelEncoder(self.df).encode() if self.encoder == 'label' else OneHotEncoder(self.df).encode()
        corr = df.to_pandas().corr(method=self.method) if isinstance(df, pl.DataFrame) else df.corr(method=self.method)
        plt.title("Correlation Matrix")
        return sns.heatmap(corr,
            cmap=sns.diverging_palette(220, 10, as_cmap=True),
            square=True, annot=True)
    