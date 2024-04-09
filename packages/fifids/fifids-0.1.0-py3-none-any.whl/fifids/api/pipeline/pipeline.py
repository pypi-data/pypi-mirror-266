import polars as pl
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import shap


class Pipeline:
    def __init__(self, df, target: str = None, time_series: bool = False):
        self.df = df.to_pandas() if isinstance(df, pl.DataFrame) else df
        self.X_train, self.X_val, self.X_test = None, None, None
        self.y_train, self.y_val, self.y_test = None, None, None
        self.target = target
        self.time_series = time_series
        self._meaningful_split()
        self.model_pipeline = None

    def _meaningful_split(self):
        # Drop nulls
        self.df.dropna(inplace=True)
        
        # Split into train, test, val
        if self.target:
            X = self.df.drop(columns=[self.target])
            y = self.df[self.target]
            if self.time_series:
                total_length = len(self.df)
                train_end = int(total_length * 0.7)
                val_end = int(total_length * 0.85)
                self.X_train, self.X_val, self.X_test = (
                    X.iloc[:train_end],
                    X.iloc[train_end:val_end],
                    X.iloc[val_end:],
                )
                self.y_train, self.y_val, self.y_test = (
                    y.iloc[:train_end],
                    y.iloc[train_end:val_end],
                    y.iloc[val_end:],
                )
            else:
                X_train, X_temp, y_train, y_temp = train_test_split(
                    X, y, test_size=0.3, random_state=42
                )
                self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
                    X_temp, y_temp, test_size=0.5, random_state=42
                )
                self.X_train, self.y_train = X_train, y_train

    def train(self):
        """
        Train a model using the training data and save it to the instance.
        """

        numeric_features = self.X_train.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        numeric_transformer = SkPipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        # Preprocessor
        preprocessor = ColumnTransformer(
            transformers=[("num", numeric_transformer, numeric_features)],
            remainder="passthrough",
        )

        model = (
            xgb.XGBRegressor() if self.y_train.dtype == "float" else xgb.XGBClassifier()
        )

        self.model_pipeline = SkPipeline(
            steps=[("preprocessor", preprocessor), ("model", model)]
        )
        self.model_pipeline.fit(self.X_train, self.y_train)

        return self

    def test(self):
        """
        Test the model using the test data and display useful metrics.
        """
        preds = self.model_pipeline.predict(self.X_test)
        mse = mean_squared_error(self.y_test, preds)
        print(f"Test MSE: {mse}")
        
        plt.figure(figsize=(12, 6))
        sns.histplot(self.y_test, color="blue", kde=True, label="True Values")
        sns.histplot(preds, color="red", kde=True, label="Predictions")
        plt.legend()
        plt.title("True Values vs Predictions")
        plt.show()

    def shapley(self):
        explainer = shap.Explainer(self.model_pipeline.named_steps["model"])
        shap_values = explainer(
            self.model_pipeline.named_steps["preprocessor"].transform(self.X_val)
        )
        shap.summary_plot(shap_values, self.X_val)
        plt.show()
