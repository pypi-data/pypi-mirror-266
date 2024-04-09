import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns


class Outliers:
    def __init__(self, df: pl.DataFrame | pd.DataFrame):
        self.df = df.to_pandas() if isinstance(df, pl.DataFrame) else df

    def show(self):
        for column_name in self.df.select_dtypes(include="number").columns:
            # KDE Plot
            plt.figure(figsize=(18, 4))
            plt.subplot(1, 3, 1)
            sns.kdeplot(data=self.df, x=column_name)
            plt.title(f"KDE Plot - {column_name}")

            # Box Plot
            plt.subplot(1, 3, 2)
            sns.boxplot(data=self.df, x=column_name)
            plt.title(f"Box Plot - {column_name}")

            # Scatter Plot to show outliers
            plt.subplot(1, 3, 3)
            plt.scatter(range(len(self.df)), self.df[column_name], alpha=0.6)
            plt.axhline(
                self.df[column_name].mean() + 3 * self.df[column_name].std(),
                color="r",
                linestyle="dashed",
            )
            plt.axhline(
                self.df[column_name].mean() - 3 * self.df[column_name].std(),
                color="r",
                linestyle="dashed",
            )
            plt.title(f"Scatter Plot with Outliers - {column_name}")

            plt.tight_layout()
            plt.show()

    def remove(self):
        original_len = len(self.df)
        for column_name in self.df.select_dtypes(include="number").columns:
            z_scores = (self.df[column_name] - self.df[column_name].mean()) / self.df[column_name].std()
            self.df = self.df[(z_scores < 3) & (z_scores > -3)]
        self.df.reset_index(drop=True, inplace=True)
        print(f"Removed {original_len - len(self.df)} outliers.")
        return self.df
