import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d
from sklearn.impute import KNNImputer
from xgbimputer import XGBImputer

class MissingValueImputer(TransformerMixin, BaseEstimator):
    def __init__(self, imputation_method='mean', group_cols=None, time_col=None, time_method='linear', prediction_model=None, threshold=0.5):
        self.imputation_method = imputation_method
        self.group_cols = group_cols
        self.time_col = time_col
        self.time_method = time_method
        self.prediction_model = prediction_model
        self.threshold = threshold
        self.imputer = None

    def fit(self, X, y=None):
        self.imputer = self._get_imputer(X)
        self.imputer.fit(X)
        return self

    def transform(self, X):
        X_copy = X.copy()
        X_copy = self._impute_missing_values(X_copy)
        return X_copy

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def _get_imputer(self, X):
        if self.imputation_method == 'mean':
            return SimpleImputer(strategy='mean')
        elif self.imputation_method == 'median':
            return SimpleImputer(strategy='median')
        elif self.imputation_method == 'most_frequent':
            return SimpleImputer(strategy='most_frequent')
        elif self.imputation_method == 'group_wise':
            return SimpleImputer(strategy='mean', missing_values=np.nan)
        elif self.imputation_method == 'time_series_spline':
            return self._time_series_spline_imputer(X)
        elif self.imputation_method == 'time_series_linear':
            return self._time_series_linear_imputer(X)
        elif self.imputation_method == 'iterative':
            return IterativeImputer(max_iter=10, random_state=42)
        elif self.imputation_method == 'prediction':
            return self._prediction_imputer(X)
        elif self.imputation_method == 'knn':
            return self._knn_imputer(X)
        elif self.imputation_method == 'xgboost':
            return self._xgboost_imputer(X)
        else:
            raise ValueError(f"Invalid imputation method: {self.imputation_method}")

    def _impute_missing_values(self, X):
        if self.imputation_method == 'omit':
            return X.dropna()
        else:
            return self.imputer.transform(X)

    def _time_series_spline_imputer(self, X):
        if self.time_col is None:
            raise ValueError("Time column must be specified for time series imputation.")

        def spline_impute(col):
            valid_idx = col.notna()
            x = col.index[valid_idx]
            y = col[valid_idx]
            f = interp1d(x, y, kind='linear')
            col[~valid_idx] = f(col[~valid_idx].index)
            return col

        if self.group_cols:
            return SimpleImputer(missing_values=np.nan, strategy=spline_impute)
        else:
            return X[self.time_col].apply(spline_impute)

    def _time_series_linear_imputer(self, X):
        if self.time_col is None:
            raise ValueError("Time column must be specified for time series imputation.")

        def linear_impute(col):
            valid_idx = col.notna()
            x = col.index[valid_idx]
            y = col[valid_idx]
            f = interp1d(x, y, kind='linear', fill_value='extrapolate')
            col[~valid_idx] = f(col[~valid_idx].index)
            return col

        if self.group_cols:
            return SimpleImputer(missing_values=np.nan, strategy=linear_impute)
        else:
            return X[self.time_col].apply(linear_impute)

    def _knn_imputer(self, X):
        if any(X.select_dtypes(include=['category', 'object'])):
            raise ValueError("KNN imputation is not supported for categorical columns.")
    
        knn_imputer = KNNImputer()
        return knn_imputer.fit_transform(X)


    def _xgboost_imputer(self, X):
        xgb_imputer = XGBImputer(with_cv=True)
        return xgb_imputer.fit_transform(X)

    def _prediction_imputer(self, X):
        if self.prediction_model is None:
            self.prediction_model = LinearRegression()

        def predict_impute(X_group):
            valid_idx = X_group.notna().all(axis=1)
            X_valid = X_group.loc[valid_idx]
            X_missing = X_group.loc[~valid_idx]

            if len(X_valid) >= len(X_group) * self.threshold:
                self.prediction_model.fit(X_valid, X_valid)
                X_missing = pd.DataFrame(self.prediction_model.predict(X_missing), index=X_missing.index, columns=X_missing.columns)
                X_group.loc[~valid_idx] = X_missing
            return X_group

        if self.group_cols:
            return SimpleImputer(missing_values=np.nan, strategy=predict_impute)
        else:
            return X.apply(predict_impute, axis=1)