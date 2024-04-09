
from typing import Literal
from .plots import Distribution, Correlation, TimeSeries
from functools import partial
import pandas as pd
import polars as pl
class Plot:
    def __init__(self, df: pl.DataFrame | pd.DataFrame, target=None, time_series=False):
        self.df = df if isinstance(df, pl.DataFrame) else pl.DataFrame(df)
        self.df = df
        self.target = target
        self.time_series = time_series

    def get_plots(self, config=None):
        """
        Create different plots for a DataFrame.
        
        @param config: Configuration for the plots.
        e.g. config = {
            "distribution": {
                "method": "hist" | "violin" | "kde" (default: hist),
                "columns": ["column1", "column2"] | None (default: all columns)
            },
            "correlation": {
                "method": "pearson" | "spearman" | "kendall" (default: pearson)
            }
        }
        
        Available plots:
        distribution: What kind of distribution is there? 
            Pass in a `method` parameter to get a specific kind of distribution.
            - hist: Histogram
            - violin: Violin plot
            - kde: Kernel Density Estimate
            
        correlation: What is the correlation between columns?
        
        """
        distribution = self._distribution()
        plots = {
            "distribution": distribution,
        }
        
        if len(self.df.columns) > 1:
            plots["correlation"] = self._correlation()
        
        if self.time_series:
            plots["time_series"] = self._time_series()
        
        return plots
    
    def _distribution(self, method: Literal['hist', 'violin', 'kde'] = 'hist', columns=None):
        if columns is None:
            columns = self.df.columns
        return Distribution(method, columns, self.df)
    
    def _correlation(self, method: Literal['pearson', 'spearman'] = 'pearson'):
        return Correlation(self.df, method)
    
    def _time_series(self):
        return TimeSeries(self.df, self.target)
    
    def __repr__(self):
        return """Use get_plots() on this to return a dictionary with the plots
    
"""
    
    