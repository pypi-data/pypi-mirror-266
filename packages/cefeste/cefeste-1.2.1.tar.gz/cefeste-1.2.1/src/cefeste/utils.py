# Utilities
import datetime as dt
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)


def get_numerical_features(df, feature_filter=None):
    """It gets a list of numerical features' names from a DataFrame excluding unwanted features' names.

    Args:
        df (pd.DataFrame): input dataframe
        feature_filter (List): list of columns that will be filtered when extracting
            numerical features.

    Returns:
        list: the list of numerical feature names
    """
    if feature_filter is None:
        feature_filter = []

    return [
        var
        for var in df.columns
        if (df[var].dtype != "O" and df[var].dtype != "category") and (var not in feature_filter)
    ]


def get_categorical_features(df, feature_filter=None):
    """It gets a list of categorical features' names from a DataFrame excluding unwanted features' names.

    Args:

    df (pd.DataFrame): input dataframe
    feature_filter (List): list of columns that will be filtered when extracting
        categorical features.

    Returns:
        list: the list of categorical feature names
    """
    if feature_filter is None:
        feature_filter = []

    categorical_feat = [
        var for var in df.columns if (df[var].dtype == "O" or df[var].dtype == "category") and var not in feature_filter
    ]

    return categorical_feat


def remove_features(df, features_to_remove):
    """Remove a list of features from the dataframe.

    Args:
        df (pd.DataFrame): Dataframe from which the features need to be removed.
        features_to_remove (list): List of strings with the labels of the columns
        to remove.
    Returns:
        (pd.DataFrame): Dataframe without columns to exclude.

    """
    before_removal = df.shape[1]
    features_to_keep = list(set(df.columns) - set(features_to_remove))
    df = df[features_to_keep]
    logging.info(f"Number of features reduced from {before_removal} to {df.shape[1]}")

    return df


def time_step(func):
    """A wrapper function to time a function.

    Args:
        func: a function to be timed.
    Returns:
        wrapper: the time that was used to run the func and the resulting shape will be printed.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        tic = dt.datetime.now()
        result = func(*args, **kwargs)
        time_taken = str(dt.datetime.now() - tic)
        logging.info(f"Completed {func.__name__}, ended at: {dt.datetime.now()}. It took {time_taken}s")
        return result

    return wrapper


def convert_Int_dataframe(db):
    """Converts feature "Int" format into "float" format of the dataset in input.

    Args:
        db (pd.DataFrame): dataset for integer converting mapping

    Returns:
        pd.DataFrame with converted int types features
    """
    return db.astype(
        {
            **{col: "float64" for col in db.columns if db[col].dtype == "Int64"},
            **{col: "float32" for col in db.columns if db[col].dtype == "Int32"},
        }
    )


def convert_Int_series(db):
    """Converts feature "Int" format into "float" format of the dataset in input.

    Args:
        db (pd.Series): pd.Series for integer converting mapping

    Returns:
        pd.Series with converted int types features
    """
    return db.astype("float64") if db.dtype == "Int64" else db.astype("float32") if db.dtype == "Int32" else db
