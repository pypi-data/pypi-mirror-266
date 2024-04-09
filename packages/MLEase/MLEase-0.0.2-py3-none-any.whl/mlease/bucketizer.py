import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.cluster import KMeans

class Bucketizer(BaseEstimator, TransformerMixin):
    def __init__(self, num_classes=None, labels=None, use_qcut=True, custom_labels=None, automatic_num_classes=False, columns=None, inplace=False):
        """
        Initialize the Bucketizer.

        Parameters:
        - num_classes (int): Number of classes to bin the data into.
        - labels (list): Labels to use for the bins.
        - use_qcut (bool): Whether to use pd.qcut or pd.cut for binning.
        - custom_labels (list): Custom labels for the bins.
        - automatic_num_classes (bool): Whether to automatically determine the number of classes based on data size.
        - columns (list): Columns to be bucketed.
        - inplace (bool): Whether to create a new column for the bucketed data or replace the original column.

        """
        self.num_classes = num_classes
        self.labels = labels
        self.use_qcut = use_qcut
        self.custom_labels = custom_labels
        self.automatic_num_classes = automatic_num_classes
        self.columns = columns
        self.inplace = inplace
        self.bins = None

    def fit(self, X, y=None):
        """
        Fit the Bucketizer to the data.

        Parameters:
        - X (DataFrame): Input data to fit the Bucketizer.

        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")

        if self.automatic_num_classes:
            self.num_classes = self._calculate_num_classes(X)

        if self.custom_labels is None:
            self.labels = list(range(self.num_classes))
        else:
            self.labels = self.custom_labels

        self.bins = {}
        for col in self.columns:
            if self.use_qcut:
                self.bins[col] = pd.qcut(X[col], self.num_classes, labels=self.labels)
            elif self.binning_method == 'equal_width':
                for col in X.select_dtypes(include=['int', 'float']).columns:
                    min_val = X[col].min()
                    max_val = X[col].max()
                    bin_edges = np.linspace(min_val, max_val, self.num_classes + 1)
                    self.bins[col] = pd.cut(X[col], bins=bin_edges, labels=self.labels, include_lowest=True)
            elif self.binning_method == 'kmeans':
                for col in X.select_dtypes(include=['int', 'float']).columns:
                    kmeans = KMeans(n_clusters=self.num_classes, random_state=0).fit(X[[col]])
                    bin_edges = np.append(kmeans.cluster_centers_ - 0.5, kmeans.cluster_centers_[-1] + 0.5)
                    self.bins[col] = pd.cut(X[col], bins=bin_edges, labels=self.labels, include_lowest=True)
            else:
                self.bins[col] = pd.cut(X[col], self.num_classes, labels=self.labels)

        return self

    def transform(self, X):
        """
        Transform the input data using the fitted Bucketizer.

        Parameters:
        - X (DataFrame): Input data to transform.

        Returns:
        - DataFrame: Transformed data.

        """
        check_is_fitted(self, 'bins')

        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")

        transformed_data = X.copy()
        for col in self.bins:
            if self.inplace:
                transformed_data[col+'_bucketed'] = self.bins[col].astype(str)
                transformed_data.drop(columns=col, inplace=True)
            else:
                transformed_data[col] = self.bins[col].astype(str)

        return transformed_data

    def fit_transform(self, X, y=None):
        """
        Fit the Bucketizer to the data and transform it in a single step.

        Parameters:
        - X (DataFrame): Input data to fit and transform.

        Returns:
        - DataFrame: Transformed data.

        """
        return self.fit(X).transform(X)

    def _calculate_num_classes(self, X):
        """
        Placeholder method to calculate the number of classes automatically.

        Parameters:
        - X (DataFrame): Input data.

        Returns:
        - int: Number of classes.

        """
        # Example of automatic num_classes calculation
        return int(np.sqrt(len(X)))
