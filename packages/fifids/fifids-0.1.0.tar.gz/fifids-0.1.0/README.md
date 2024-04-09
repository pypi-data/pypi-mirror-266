# Fifi
## data science for swiss cheese brains
---

Fifi is a pypi package for quick eda and modelling made specifically for use with Jupyter Notebooks.
Use `??` as much as possible to see the code and adapt it for your needs. The package will guide you through the usual EDA process.

The package is meant be a source of cool plots or workflows and be able to use them within Jupyter without having to look at documentation every time.

## Installation

```bash
pip install fifi
```

## Usage

```python
from fifi import Fifi
import pandas as pd
import polars as pl

df = pd.read_csv("data.csv")
# OR POLARS
df = pl.read_csv("data.csv")
# Note from author: eventually, right now it breaks with polars, but I'm working on it

# Specify the target column and if the data is time series or not
# Time series enables a branch with more plots and a different train/test split
fifi = Fifi(df, target="target_column", time_series=True)

fifi.describe()
# OR
fifi.plots()
# OR
fifi.outliers()
# OR
fifi.pipeline()
```

Once you call a function, it will usually print something to guide you through the process. You can also use the `??` to see the code.
