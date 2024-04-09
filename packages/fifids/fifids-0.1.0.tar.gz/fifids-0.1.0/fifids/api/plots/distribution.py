import seaborn as sns
import matplotlib.pyplot as plt

class Distribution:
    def __init__(self, method, columns, df):
        self.method = method
        self.columns = columns
        self.df = df
    
    def show(self):
        if self.method == 'hist':
            return self._hist(self.df)
    
    def _hist(self, df):
        for col in self.columns:
            sns.histplot(df[col])
            plt.title(f"Distribution of {col}")
            plt.show()