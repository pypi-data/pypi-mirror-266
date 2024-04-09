from sklearn.base import TransformerMixin, BaseEstimator
import pandas as pd
import numpy as np

class ColumnExtractor(object):
    """Simple Class for extracting columns from a database.

    To be used in pipeline to apply the feature selection or elimination results.
    """

    def __init__(self, cols):
        """Initialize the class with colums to keep."""
        self.cols = cols

    def transform(self, X):
        """Apply to a pd.DataFrame."""
        return X[self.cols]

    def fit(self, X, y=None):
        """No Fitter."""
        return self

    def fit_transform(self, X, y=None):
        """Apply the the transform."""
        return self.transform(X)


class ColumnRenamer(object):
    """Simple Class for rename columns from a database.

    To be used in pipeline after transformers to allow further steps.
    """

    def __init__(self, col_names):
        """Initialize the class with columns name."""
        self.col_names = col_names

    def transform(self, X):
        """Apply to a np.array or pd.DataFrame."""
        X = pd.DataFrame(X, columns=self.col_names)
        return X

    def fit(self, X, y=None):
        """No Fitter."""
        return self

    def fit_transform(self, X, y=None):
        """Apply the the transform."""
        return self.transform(X)


class Categorizer:
    """Simple Class for trasform columns from a database from object dtype to category.

    To be used in pipeline before the feature elimination if the selected model used categorical features.
    """

    def __init__(self, feat_to_check=None):
        """Initialize the class with the columns to be considered. If None all are checked."""
        self.feat_to_check = feat_to_check
        self._fitted = False
        return

    def fit(self, X, y=None):
        """Identify the columns with dtypes object from the input pd.DataFrame."""
        self._fitted = True
        if self.feat_to_check is None:
            self.feat_to_check = X.columns

        self._cols_to_categorize = [x for x in X[self.feat_to_check].columns if X[x].dtype == "O"]
        return

    def transform(self, X):
        """Transform the columns identified of a pd.DataFrame in type category."""
        if not self._fitted:
            raise ValueError("Categorizer not fitted. Run fit method before.")

        for x in self._cols_to_categorize:
            X[x] = X[x].astype("category")

        return X

    def fit_transform(self, X, y=None):
        """Identify and trasform the columns with dtypes object to category for the input pd.DataFrame."""
        self._fitted = True

        if self.feat_to_check is None:
            self.feat_to_check = X.columns

        self._cols_to_categorize = [x for x in X[self.feat_to_check].columns if X[x].dtype == "O"]

        for x in self._cols_to_categorize:
            X[x] = X[x].astype("category")

        return X



class Dummitizer(BaseEstimator, TransformerMixin):
    """Simple Class for create dummy 0 or 1 where 1 is: the orginal feature was different from the base value (Default 0).

    To be used in pipeline.
    """

    def __init__(self, columns=None, base_value=0):
        """Initialize the class with columns name."""
        self.columns = columns
        self.base_value = base_value
  
    def fit(self, X, y=None):
        """No fitting needed."""
        return self

    def transform(self, X):
        """Create dummy for the features selected."""
        columns = self.columns
        if self.columns is None:
            columns = X.columns
        X_copy = X.copy()
        X_copy[columns] = (X_copy[columns] != self.base_value).astype('int')
        return X_copy

    def fit_transform(self, X, y=None):
        """Apply the the transform."""
        return self.transform(X)
    
class ManageOutlier(BaseEstimator, TransformerMixin):
    """Simple Class for manage outlier over the upper bound.

    To be used in pipeline.
    """

    def __init__(self, columns=None, left_quantile = 0.25, right_quantile = 0.75, iqr_multiplier=1.5, side='both'):
        """Initialize the class with columns name."""
        self.columns = columns
        self.iqr_multiplier = iqr_multiplier
        self.side = side
        self.manage_upper=True
        self.manage_lower=True
        self.left_quantile=left_quantile
        self.right_quantile=right_quantile
        if side == "upper":
            self.manage_lower=False
        elif side == "lower":
            self.manage_upper=False
  
    def fit(self, X, y=None):
        """Calculate upper and lower limits based on IQR."""
        columns = self.columns
        if self.columns is None:
            columns = X.columns
        
        X_copy = X.copy()[columns]
        q1 = X_copy.quantile(self.left_quantile)
        q3 = X_copy.quantile(self.right_quantile)
        iqr = q3-q1
        self.upper_lim = np.inf
        self.lower_lim = -np.inf
        if self.manage_upper:
            self.upper_lim= q3 + self.iqr_multiplier*iqr
        if self.manage_lower:
            self.lower_lim= q1 - self.iqr_multiplier*iqr


        return self

    def transform(self, X):
        """Clip values to the specified upper and lower limits."""
        columns = self.columns
        if self.columns is None:
            columns = X.columns
        X_copy = X.copy()[columns]
        X_copy = X_copy.clip(lower = self.lower_lim, upper=self.upper_lim, axis=1)
        return X_copy

    def fit_transform(self, X, y=None):
        """Fit and trasform"""
        return self.fit(X).transform(X)
    
    
class LogTransformer(BaseEstimator, TransformerMixin):
    """Simple Class for manage outlier over the upper bound.

    To be used in pipeline.
    """

    def __init__(self, columns=None, log_base=10):
        """Initialize the class with columns name."""
        self.columns = columns
        self.log_base = log_base

  
    def fit(self, X, y=None):
        """No fitting needed."""
        return self

    def transform(self, X):
        """Trasform to log"""
        columns = self.columns
        if self.columns is None:
            columns = X.columns
        X_copy = X.copy()[columns]
        X_copy = np.log(X_copy)/np.log(self.log_base)
        return X_copy

    def fit_transform(self, X, y=None):
        """Fit and trasform"""
        return self.transform(X)