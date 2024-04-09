import pandas as pd
import numpy as np
from scipy.stats import chi2
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor

class OutlierRemover(TransformerMixin, BaseEstimator):
    def __init__(self, scaler =  PowerTransformer(), sigma=True, sigma_factor=3, iqr=False,iqr_factor=0.25, mahalanobis=False, anomaly_detection=None, threshold=0.05):
        """
        Initialize the OutlierRemover object.

        Parameters:
        scaler (sklearn.preprocessing.Scaler): The scaler to use for feature scaling. Defaults to PowerTransformer().
        sigma (bool): If True, remove outliers based on sigma values (mean +/- 3 * std).
        sigma_factor (float): The number of standard deviations to use for sigma-based outlier removal.
        iqr (bool): If True, remove outliers based on Interquartile Range (IQR).
        iqr_factor (float): The factor to use for IQR-based outlier removal (q1 - iqr_factor * iqr, q3 + iqr_factor * iqr).
        mahalanobis (bool): If True, remove outliers based on Mahalanobis distance.
        anomaly_detection (str): The name of the anomaly detection algorithm to use ('isolation_forest', 'oneclass_svm', 'elliptic_envelope', 'local_outlier_factor').
        threshold (float): The contamination threshold for the anomaly detection algorithm.
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        if not 0<=iqr_factor<=1:
            raise ValueError("IQR Factor must be between 0 and 1")
        if not sigma_factor>0:
            raise ValueError("Sigma Factor must be greater than 0")
        self.sigma = sigma
        self.sigma_factor = sigma_factor
        self.iqr = iqr
        self.iqr_factor = iqr_factor
        self.mahalanobis = mahalanobis
        self.anomaly_detection = anomaly_detection
        self.threshold = threshold
        self.scaler = scaler
        self.continuous_columns = None
        self.cov_matrix = None

    def fit(self, X, y=None):
        """
        Fit the OutlierRemover to the input data.

        Parameters:
        X (pandas.DataFrame): The input data.
        y (None): Not used, included for compatibility with scikit-learn.

        Returns:
        self (OutlierRemover): The fitted OutlierRemover object.
        """
        self.continuous_columns = X.select_dtypes(include=[np.number]).columns
        self.cov_matrix = X[self.continuous_columns].cov()

        # Remove outliers based on sigma values (mean +/- 3 * std)
        if self.sigma:
            for col in self.continuous_columns:
                mean = X[col].mean()
                std = X[col].std()
                X = X[(X[col] >= mean - self.sigma_factor * std) & (X[col] <= mean + self.sigma_factor * std)]

        # Remove outliers based on Interquartile Range (IQR)
        if self.iqr:
            for col in self.continuous_columns:
                q1 = X[col].quantile(self.iqr_factor)
                q3 = X[col].quantile(1 - self.iqr_factor)
                iqr = q3 - q1
                X = X[(X[col] >= q1 - 1.5 * iqr) & (X[col] <= q3 + 1.5 * iqr)]

        # Remove outliers based on Mahalanobis distance
        if self.mahalanobis:
            m_distances = X[self.continuous_columns].apply(self.mahalanobis_distance, axis=1)
            threshold = chi2.ppf(1 - self.threshold, len(self.continuous_columns))
            X = X[m_distances <= np.sqrt(threshold)]

        # Remove outliers based on the specified anomaly detection algorithm
        if self.anomaly_detection == 'isolation_forest':
            outlier_model = IsolationForest(contamination=self.threshold, behaviour='new')
            outlier_model.fit(X[self.continuous_columns])
            X = X[outlier_model.predict(X[self.continuous_columns]) == 1]

        elif self.anomaly_detection == 'oneclass_svm':
            self.scaler.fit(X[self.continuous_columns])
            X_scaled = self.scaler.transform(X[self.continuous_columns])
            outlier_model = OneClassSVM(nu=self.threshold)
            outlier_model.fit(X_scaled)
            X = X[outlier_model.predict(X[self.continuous_columns]) == 1]

        elif self.anomaly_detection == 'elliptic_envelope':
            self.scaler.fit(X[self.continuous_columns])
            X_scaled = self.scaler.transform(X[self.continuous_columns])
            outlier_model = EllipticEnvelope(contamination=self.threshold)
            outlier_model.fit(X_scaled)
            X = X[outlier_model.predict(X_scaled) == 1]

        elif self.anomaly_detection == 'local_outlier_factor':
            outlier_model = LocalOutlierFactor(contamination=self.threshold)
            outlier_model.fit(X[self.continuous_columns])
            X = X[outlier_model.predict(X[self.continuous_columns]) == 1]

        # Fit the standard scaler to the cleaned data
        self.scaler.fit(X[self.continuous_columns])
        return self

    def transform(self, X):
        """
        Transform the input data by removing outliers and scaling the continuous features.

        Parameters:
        X (pandas.DataFrame): The input data.

        Returns:
        X_copy (pandas.DataFrame): The transformed data with outliers removed and continuous features scaled.
        """
        X_copy = X.copy()
        X_copy[self.continuous_columns] = self.scaler.transform(X_copy[self.continuous_columns])
        return X_copy

    def fit_transform(self, X, y=None):
        """
        Fit the OutlierRemover to the input data and transform it.

        Parameters:
        X (pandas.DataFrame): The input data.
        y (None): Not used, included for compatibility with scikit-learn.

        Returns:
        X_transformed (pandas.DataFrame): The transformed data with outliers removed and continuous features scaled.
        """
        self.fit(X)
        return self.transform(X)

    def mahalanobis_distance(self, x):
        """
        Calculate the Mahalanobis distance for a given data point.

        Parameters:
        x (pandas.Series): The data point for which to calculate the Mahalanobis distance.

        Returns:
        m_distance (float): The Mahalanobis distance for the data point.
        """
        x_minus_mu = x - np.mean(x)
        inv_cov = np.linalg.inv(self.cov_matrix)
        m_distance = np.sqrt(np.dot(np.dot(x_minus_mu, inv_cov), x_minus_mu.T))
        return m_distance
