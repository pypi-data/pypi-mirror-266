# AUC and corr
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import roc_auc_score

from cefeste.utils import get_categorical_features
from cefeste.selection.multivariate import numerical_categorical_correlation


# @time_step
def find_not_explanatory(
    X_train, X_test, y_train, y_test, threshold=0.05, algo_type="classification", dim_cat_threshold=10
):
    """Retrieve the list of features that are not useful in the model.

    Args:
        X_train (pd.DataFrame): Feature Dataset for the train set
        X_test (pd.DataFrame): Feature Dataset for the test set
        y_train (pd.Series): target for the train set
        y_test (pd.Series): target for the test set
        threshold(float): minimum performance acceptable. Gini for classification, Correlation for regression.
        algo_type (str): 'classification' or 'regression', 'multiclass'. Define the type of model
        dim_cat_threshold (int): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (list, pd.DataFrame): list of not useful features, dataframe of the performance for each feature
    """
    if algo_type not in ("classification", "regression", "multiclass"):
        raise ValueError("algo_type must be either 'classification' or 'regression' or 'multiclass")
    auc = (1 + threshold) / 2
    if algo_type == "classification":
        return find_not_explanatory_auc(
            X_train, X_test, y_train, y_test, min_auc_tgt=auc, dim_cat_threshold=dim_cat_threshold
        )
    elif algo_type == "regression":
        return find_not_explanatory_corr(X_train, X_test, y_train, y_test, min_corr_tgt=threshold)
    else:
        return find_not_explanatory_auc_multi(
            X_train, X_test, y_train, y_test, min_auc_tgt=auc, dim_cat_threshold=dim_cat_threshold
        )


def find_not_explanatory_auc(X_train, X_test, y_train, y_test, min_auc_tgt=0.525, dim_cat_threshold=10):
    """Retrieve the list of features that are not useful in a classification model.

    Args:
        X_train (pd.DataFrame): Feature Dataset for the train set
        X_test (pd.DataFrame): Feature Dataset for the test set
        y_train (pd.Series): target for the train set
        y_test (pd.Series): target for the test set
        min_auc_tgt (float): minimum AUROC
        dim_cat_threshold (int): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (list, pd.DataFrame): list of not useful features, dataframe of the performance (AUC) for each feature
    """
    with_test = (X_test is not None) & (y_test is not None)
    results = dict()

    train_col_pb = tqdm(X_train.columns, file=sys.stdout, desc="Performing find_not_explanatory", ncols=100, leave=True)
    for ix, col in enumerate(train_col_pb):
        clf = DecisionTreeClassifier(max_depth=5, min_samples_leaf=0.03)
        if col in get_categorical_features(X_train):
            if X_train[col].nunique() > dim_cat_threshold:
                regressor_tr = X_train[[col]].copy()
                if with_test:
                    regressor_te = X_test[[col]].copy()
                values_cat = list(
                    regressor_tr.groupby(col, sort=False)[col].count().sort_values(ascending=False).index
                )[:dim_cat_threshold]
                for val in values_cat:
                    regressor_tr[col + "_" + str(val)] = (regressor_tr[col] == val).astype("int")
                    if with_test:
                        regressor_te[col + "_" + str(val)] = (regressor_te[col] == val).astype("int")
                regressor_tr = regressor_tr.drop(columns=col)
                if with_test:
                    regressor_te = regressor_te.drop(columns=col)
            else:
                ohe = OneHotEncoder(sparse=False, handle_unknown="ignore")
                regressor_tr = ohe.fit_transform(X_train[[col]])
                if with_test:
                    regressor_te = ohe.transform(X_test[[col]])
        else:
            regressor_tr = X_train[[col]].fillna(X_train[col].median())
            if with_test:
                regressor_te = X_test[[col]].fillna(X_test[col].median())
        if ix == len(X_train.columns) - 1:
            train_col_pb.set_description("Completed find_not_explanatory", refresh=True)

        clf.fit(regressor_tr, y_train)
        y_pred_tr = clf.predict_proba(regressor_tr)[:, 1]
        if with_test:
            y_pred_te = clf.predict_proba(regressor_te)[:, 1]
            results[col] = [roc_auc_score(y_train, y_pred_tr), roc_auc_score(y_test, y_pred_te)]
        else:
            results[col] = roc_auc_score(y_train, y_pred_tr)

    drop_list = [x for x, y in results.items() if np.min(y) < min_auc_tgt]
    perf = pd.DataFrame()
    perf["name"] = results.keys()
    perf["perf"] = results.values()
    if with_test:
        perf[["train", "test"]] = perf.perf.apply(pd.Series)
        perf["perf"] = perf[["train", "test"]].min(axis=1)

    return drop_list, perf


def find_not_explanatory_auc_multi(X_train, X_test, y_train, y_test, min_auc_tgt=0.525, dim_cat_threshold=10):
    """Retrieve the list of features that are not useful in a classification model.

    Args:
        X_train (pd.DataFrame): Feature Dataset for the train set
        X_test (pd.DataFrame): Feature Dataset for the test set
        y_train (pd.Series): target for the train set
        y_test (pd.Series): target for the test set
        min_auc_tgt (float): minimum AUROC
        dim_cat_threshold (int): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (list, pd.DataFrame): list of not useful features, dataframe of the performance (AUC) for each feature
    """
    with_test = (X_test is not None) & (y_test is not None)
    results = dict()

    train_col_pb = tqdm(X_train.columns, file=sys.stdout, desc="Performing find_not_explanatory", ncols=100, leave=True)
    for ix, col in enumerate(train_col_pb):
        clf = DecisionTreeClassifier(max_depth=5, min_samples_leaf=0.03)
        if col in get_categorical_features(X_train):
            if X_train[col].nunique() > dim_cat_threshold:
                regressor_tr = X_train[[col]].copy()
                if with_test:
                    regressor_te = X_test[[col]].copy()
                values_cat = list(
                    regressor_tr.groupby(col, sort=False)[col].count().sort_values(ascending=False).index
                )[:dim_cat_threshold]
                for val in values_cat:
                    regressor_tr[col + "_" + str(val)] = (regressor_tr[col] == val).astype("int")
                    if with_test:
                        regressor_te[col + "_" + str(val)] = (regressor_te[col] == val).astype("int")
                regressor_tr = regressor_tr.drop(columns=col)
                if with_test:
                    regressor_te = regressor_te.drop(columns=col)
            else:
                ohe = OneHotEncoder(sparse=False, handle_unknown="ignore")
                regressor_tr = ohe.fit_transform(X_train[[col]])
                if with_test:
                    regressor_te = ohe.transform(X_test[[col]])
        else:
            regressor_tr = X_train[[col]].fillna(X_train[col].median())
            if with_test:
                regressor_te = X_test[[col]].fillna(X_test[col].median())

        clf.fit(regressor_tr, y_train)
        y_pred_tr = clf.predict_proba(regressor_tr)
        if with_test:
            y_pred_te = clf.predict_proba(regressor_te)
            results[col] = [
                roc_auc_score(y_train, y_pred_tr, multi_class="ovr"),
                roc_auc_score(y_test, y_pred_te, multi_class="ovr"),
            ]
        else:
            results[col] = roc_auc_score(y_train, y_pred_tr, multi_class="ovr")
        if ix == len(X_train.columns) - 1:
            train_col_pb.set_description("Completed find_not_explanatory", refresh=True)

    drop_list = [x for x, y in results.items() if np.min(y) < min_auc_tgt]
    perf = pd.DataFrame()
    perf["name"] = results.keys()
    perf["perf"] = results.values()
    if with_test:
        perf[["train", "test"]] = perf.perf.apply(pd.Series)
        perf["perf"] = perf[["train", "test"]].min(axis=1)

    return drop_list, perf


def find_not_explanatory_corr(X_train, X_test, y_train, y_test, min_corr_tgt=0.05):
    """Retrieve the list of features that are not useful in a regression model.

    Args:
        X_train (pd.DataFrame): Feature Dataset for the train set
        X_test (pd.DataFrame): Feature Dataset for the test set
        y_train (pd.Series): target for the train set
        y_test (pd.Series): target for the test set
        min_corr_tgt (float): minimum correlation
    Returns:
        (list, pd.DataFrame): list of not useful features, dataframe of the performance (Correlation) for each feature
    """
    # to be done
    with_test = (X_test is not None) & (y_test is not None)
    results = dict()

    train_col_pb = tqdm(X_train.columns, file=sys.stdout, desc="Performing find_not_explanatory", ncols=100, leave=True)
    for ix, col in enumerate(train_col_pb):
        if col in get_categorical_features(X_train):
            if with_test:
                results[col] = [
                    numerical_categorical_correlation(X_train[col].astype('object').fillna('Missing'), y_train),
                    numerical_categorical_correlation(X_test[col].astype('object').fillna('Missing'), y_test),
                ]
            else:
                results[col] = numerical_categorical_correlation(X_train[col].astype('object').fillna('Missing'), y_train)
        else:
            if with_test:
                results[col] = [
                    np.abs(X_train[col].fillna(0).corr(y_train)),
                    np.abs(X_test[col].fillna(0).corr(y_test)),
                ]
            else:
                results[col] = np.abs(X_train[col].fillna(0).corr(y_train))
        if ix == len(X_train.columns) - 1:
            train_col_pb.set_description("Completed find_not_explanatory", refresh=True)

    drop_list = [x for x, y in results.items() if np.min(y) < min_corr_tgt]
    perf = pd.DataFrame()
    perf["name"] = results.keys()
    perf["perf"] = results.values()
    if with_test:
        perf[["train", "test"]] = perf.perf.apply(pd.Series)
        perf["perf"] = perf[["train", "test"]].min(axis=1)

    return drop_list, perf
