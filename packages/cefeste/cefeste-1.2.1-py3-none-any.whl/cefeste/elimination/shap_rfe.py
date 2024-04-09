import pandas as pd
import numpy as np
import shap
from sklearn.metrics import roc_auc_score, r2_score, balanced_accuracy_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, GroupKFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import re
from cefeste.utils import remove_features, time_step
from functools import reduce
import warnings
import logging

logging.basicConfig(level=logging.INFO)


@time_step
def Shap_RFE_full(
    X_train,
    y_train,
    model,
    grid,
    cv_funct=RandomizedSearchCV,
    cv_scoring="auto",
    n_iter=20,
    manage_groups=False,
    groups=None,
    cv_type=StratifiedKFold(5, random_state=42, shuffle=True),
    algo_type="classification",
    step_size=0.1,
    min_n_feat_step=5,
    final_n_feature=1,
    verbose=True,
    write_final=False,
    write_substep=False,
    use_ohe=True,
    categorical_features_list_ohe=None,
    dim_cat_threshold=10,
):
    """Recursive Feature Elimination Process with Hyperparameters grid search.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        y_train (pd.Series): target set.
        model: classifier or regressor in sklearn API class.
        grid (dict): hyperparameters grid.
        cv_funct: function or class for the Cross Validation. Defaults to RandomizedSearchCV.
        n_iter (int, optional): number of iteration, i.e. set of hyperparams tested in Cross Validation. Defaults to 20.
        manage_groups (bool, optional): determines if there is a feature whose groups have to be kept joined in CV. Defaults to False.
        groups (pd.Series, optional): feature whose groups have to be kept joined in CV. Defaults to None.
        cv_type : function or class for defining the CV sets. Defaults to StratifiedKFold(5, random_state=42, shuffle=True).
        algo_type (str, optional): "classification", "multiclass", "regression", describes the problem type.
            "classification" has to be used only for binary classification. Defaults to "classification".
        step_size (int or float, optional): determines how many features to remove at each step.
            Fixed int or percentage of total features. Defaults to 0.1.
        min_n_feat_step (int, optional): min number of feature to remove at each step. Defaults to 5.
        final_n_feature (int, optional): number of features of the last model. Defaults to 1.
        verbose (bool, optional): If True print a log of information. Defaults to True.
        write_final (bool, optional): If True it saves in the current directory the final report that can be used for quick start. Defaults to False.
        write_substep (bool, optional): If True it saves in the current directory the report after SHAP_RFE that can be used for quick start. Defaults to False.
        use_ohe (bool, optional): determines whether to use One Hot Encoding on categorical features or not. Defaults to True.
        categorical_features_list_ohe (list, optional): list of categorical features for One Hot Encoding. Defaults to None.
        dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.

    Return:
    pd.DataFrame: Report of the detail and result of each step of FE and Grid Search.
    """
    if groups is None:
        groups = pd.Series()

    if algo_type not in ["classification", "regression", "multiclass"]:
        raise ValueError("algo_type argument must be one of ['classification', 'regression', 'multiclass']")

    if (algo_type == "regression") and (str(cv_type.__class__()).startswith("StratifiedKFold")):
        raise ValueError("Fold Cross Validation uncorrect for regression algorithm, use KFold() or GroupKFold()")

    if cv_scoring == "auto":
        if algo_type == "classification":
            cv_scoring = "roc_auc"
        elif algo_type == "regression":
            cv_scoring = "r2"
        elif algo_type == "multiclass":
            cv_scoring = "balanced_accuracy"

    # Define the algo
    try:
        CVSel_algo = cv_funct(model, grid, n_iter=n_iter, cv=cv_type, scoring=cv_scoring)
    except Exception:
        CVSel_algo = cv_funct(model, grid, cv=cv_type, scoring=cv_scoring)  # for GridSearchCV

    # Define the groups for Cross Validation
    if manage_groups:
        if len(groups) != len(X_train):
            raise ValueError(
                "dataset to be performed shap and groups-Series don't have the same number of rows ({0},{1})".format(
                    len(X_train), len(groups)
                )
            )
        number_splits = cv_type.n_splits
        CVSel_algo.cv = GroupKFold(number_splits).split(X_train, y_train, groups)
    else:
        number_splits = None

    # Perform Shap Recursive Feature Elimination
    report = Shap_RFE(
        X_train,
        y_train,
        CVSel_algo,
        algo_type=algo_type,
        step_size=step_size,
        min_n_feat_step=min_n_feat_step,
        final_n_feature=final_n_feature,
        verbose=verbose,
        write=write_substep,
        use_ohe=use_ohe,
        categorical_features_list_ohe=categorical_features_list_ohe,
        number_splits=number_splits,
        dim_cat_threshold=dim_cat_threshold,
    )
    # Train the final model
    X_train = X_train[report["feat_select"].iloc[-1]]
    initial_feat_n = X_train.shape[1]
    if manage_groups:
        CVSel_algo.cv = GroupKFold(number_splits).split(X_train, y_train, groups)
    X_train_tsf = X_train.copy()
    if use_ohe:
        cats_feat = list(set(categorical_features_list_ohe) & set(X_train.columns))
        for col in cats_feat:
            if X_train_tsf[col].nunique() > dim_cat_threshold:
                values_cat = list(X_train_tsf.groupby(col, sort=False)[col].count().sort_values(ascending=False).index)[
                    :dim_cat_threshold
                ]
                for val in values_cat:
                    X_train_tsf[col + "_" + str(val)] = (X_train_tsf[col] == val).astype("int")
                X_train_tsf = X_train_tsf.drop(columns=col)
                cats_feat.remove(col)
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse=False), cats_feat),
            ],
            remainder="passthrough",
        )
        preprocessor.fit(X_train_tsf)
        feat_names = preprocessor.get_feature_names_out()
        feat_names = [re.sub(r"((remainder)|(cat))__", "", x) for x in feat_names]
        X_train_tsf = pd.DataFrame(preprocessor.transform(X_train_tsf), columns=feat_names)
    else:
        X_train_tsf[X_train_tsf.select_dtypes(["object"]).columns] = X_train_tsf.select_dtypes(["object"]).apply(
            lambda x: x.astype("category")
        )
    CVSel_algo.fit(X_train_tsf, y_train)

    model = CVSel_algo.best_estimator_
    # Get measure
    if algo_type == "classification":
        train_model_score = roc_auc_score(y_train, CVSel_algo.predict_proba(X_train_tsf)[:, 1])
    elif algo_type == "regression":
        train_model_score = r2_score(y_train, CVSel_algo.predict(X_train_tsf))
    elif algo_type == "multiclass":
        train_model_score = balanced_accuracy_score(y_train, CVSel_algo.predict(X_train_tsf))

    valid_model_score = CVSel_algo.best_score_
    report_step = pd.DataFrame(
        {
            "n_feat": [initial_feat_n],
            "train_score": [train_model_score],
            "valid_score": [valid_model_score],
            "n_feat_to_remove": [0],
            "feat_used": [list(X_train.columns)],
            "feat_to_remove": [[]],
            "feat_select": [list(X_train.columns)],
            "best_estimator": [model],
        }
    )
    report = pd.concat([report, report_step]).reset_index(drop=True)

    if write_final:
        report.to_csv("rsfe_report_final.csv", index=False)

    return report


@time_step
def Shap_RFE(
    X_train,
    y_train,
    CVSel_algo,
    algo_type="classification",
    step_size=0.1,
    min_n_feat_step=5,
    final_n_feature=1,
    verbose=True,
    write=True,
    use_ohe=False,
    categorical_features_list_ohe=None,
    manage_groups=False,
    groups=None,
    number_splits=5,
    dim_cat_threshold=10,
):
    """Recursive Feature Elimination Process with Hyperparameters grid search.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        y_train (pd.Series): target set.
        CVSel_algo: class that include the classifier/regresor, grid search and detail of CV selection.
        algo_type: "classification", "regression" or "multiclass", describes the problem type. Defaults to "classification".
        step_size (int or float): determines how many features to remove at each step.
            Fixed int or percentage of total features. Defaults to 0.1.
        min_n_feat_step (int): min number of feature to remove at each step. Defaults to 5.
        final_n_feature (int): number of features of the last model. Defaults to 1.
        verbose (bool): If True print a log of information. Defaults to True.
        write (bool): If True it saves in the current directory the report that can be used for quick start. Defaults to True.
        use_ohe (bool, optional): determines whether to use One Hot Encoding on categorical features or not. Defaults to False.
        categorical_features_list_ohe (list, optional): list of categorical features for One Hot Encoding. Defaults to None.
        manage_groups (bool, optional): determines if there is a feature whose groups have to be kept joined in CV. Defaults to False.
        groups (pd.Series, optional): feature whose groups have to be kept joined in CV. Defaults to None.
        number_splits (int, optional): number of splits in CV for GroupFold. Defaults to 5.
        dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.


    Return:
    pd.DataFrame: Report of the detail and result of each step of FE and Grid Search.
    """
    initial_feat_n = X_train.shape[1]
    if use_ohe:
        cats_feat = list(set(X_train.columns) & set(categorical_features_list_ohe))

        if algo_type == "classification":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_AUC(
                X_train, y_train, CVSel_algo, categorical_feature=cats_feat, dim_cat_threshold=dim_cat_threshold
            )
        elif algo_type == "regression":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_R2(
                X_train, y_train, CVSel_algo, categorical_feature=cats_feat, dim_cat_threshold=dim_cat_threshold
            )
        elif algo_type == "multiclass":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_BalAcc(
                X_train, y_train, CVSel_algo, categorical_feature=cats_feat, dim_cat_threshold=dim_cat_threshold
            )
    else:
        if algo_type == "classification":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_AUC(
                X_train,
                y_train,
                CVSel_algo,
            )
        elif algo_type == "regression":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_R2(
                X_train,
                y_train,
                CVSel_algo,
            )
        elif algo_type == "multiclass":
            shap_importance, model, train_model_score, valid_model_score = get_Shap_BalAcc(
                X_train,
                y_train,
                CVSel_algo,
            )

    X_train, feat_to_remove = get_new_X(X_train, shap_importance, step_size, min_n_feat_step, final_n_feature)
    report = pd.DataFrame(
        {
            "n_feat": [initial_feat_n],
            "train_score": [train_model_score],
            "valid_score": [valid_model_score],
            "n_feat_to_remove": [len(feat_to_remove)],
            "feat_used": [feat_to_remove + list(X_train.columns)],
            "feat_to_remove": [feat_to_remove],
            "feat_select": [list(X_train.columns)],
            "best_estimator": [model],
        }
    )
    if verbose:
        logging.info(
            f"Train Score: {train_model_score}, Valid Score: {valid_model_score}, features to remove: {feat_to_remove}"
        )
    if X_train.shape[1] > final_n_feature:
        if manage_groups:
            CVSel_algo.cv = GroupKFold(number_splits).split(X_train, y_train, groups)
        report_step = Shap_RFE(
            X_train,
            y_train,
            CVSel_algo,
            algo_type,
            step_size,
            min_n_feat_step,
            final_n_feature,
            verbose,
            write,
            use_ohe,
            categorical_features_list_ohe,
            manage_groups,
            groups,
            number_splits=number_splits,
            dim_cat_threshold=dim_cat_threshold,
        )
        report = pd.concat([report, report_step])

    if write:
        report.to_csv(f"rsfe_report_until{X_train.shape[1]}", index=False)

    return report


def get_Shap(X_train, model, categorical_shap_ohe=False, categorical_feature=None, y_train=None):
    """Get Features' Shapley Value.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        model: the fitted best estimator of the CV Selection.
        categorical_shap_ohe (bool, optional): determines if there are columns coming from OHE. Defaults to False.
        categorical_feature (list, optional): list of categorical features before OHE. Defaults to [].
        y_train (pd.Series, optional): target set. Defaults to None.
    Returns:
        pd.DataFrame: Shap DataFrame.
    """
    if categorical_feature is None:
        categorical_feature = []

    # Get Shap
    feature_names = X_train.columns
    using_features_importance = False
    try:
        shap_values = shap.TreeExplainer(model).shap_values(X_train)
    except Exception:
        try:
            # For Support Vector Machine and other no-Tree Algorithms
            n_clusters = max(10, min(1000, int(X_train.shape[0] / 100)))
            model.fit(X_train.values, y_train.values)
            shap_values = shap.KernelExplainer(model.predict, shap.kmeans(X_train, n_clusters)).shap_values(X_train)
        except Exception:
            warnings.warn("shap inconsistent with this numpy version. Using feature_importance_ attribute")
            # For computing features importance due to numpy version issues
            feature_importances = model.feature_importances_
            using_features_importance = True

    if using_features_importance:
        shap_importance = pd.DataFrame({"feature": feature_names, "shap_importance": feature_importances})
    else:
        # For (multi) classification
        if isinstance(shap_values, list):
            db_list = list()
            for i in range(len(shap_values)):
                db_list.append(
                    pd.DataFrame(
                        {"feature": feature_names, "shap_importance_" + str(i): np.abs(shap_values[i]).mean(axis=0)}
                    )
                )
            shap_importance = (
                reduce(lambda left, right: pd.merge(left, right, how="outer", on="feature"), db_list)
                .set_index("feature")
                .assign(shap_importance=lambda x: x.sum(axis=1))
                .loc[:, "shap_importance"]
                .reset_index()
            )
        # For regression and (some - depending on the classifier) binary classification
        elif isinstance(shap_values, np.ndarray):
            shap_importance = pd.DataFrame(
                {"feature": feature_names, "shap_importance": np.abs(shap_values).mean(axis=0)}
            )

    # For categorical features one-hot-encoded sum the shap values referring the same pivot feature
    if categorical_shap_ohe:
        for i in categorical_feature:
            shap_importance.loc[shap_importance.feature.str.startswith(i)] = shap_importance.loc[
                shap_importance.feature.str.startswith(i)
            ].assign(
                feature=i,
                shap_importance=shap_importance.loc[shap_importance.feature.str.startswith(i), "shap_importance"].sum(),
            )
        shap_importance = shap_importance.drop_duplicates().dropna().reset_index(drop=True)
    shap_importance.sort_values(by=["shap_importance"], ascending=True, inplace=True)
    return shap_importance


def get_Shap_AUC(X_train, y_train, CVSel_algo, categorical_feature=None, dim_cat_threshold=10):
    """Get the AUC of the model and Features' Shapley Value.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        y_train (pd.Series): target set.
        CVSel_algo: class that include the classifier, grid search and detail of CV selection.
        categorical_feature (list, optional): list of categorical feature to be preprocessed. Defaults to None.
        dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (pd.DataFrame, classifier, float, float): Shap DataFrame, Best Classifier, Train and Valid AUC.
    """
    if categorical_feature is None:
        categorical_feature = []

    # Estimate
    categorical_shap_ohe = False
    X_train_tsf = X_train.copy()
    if len(categorical_feature) > 0:
        # Categorical Preprocessing Hot-One-Encoder
        cats_feat = categorical_feature.copy()
        for col in cats_feat:
            if X_train_tsf[col].nunique() > dim_cat_threshold:
                values_cat = list(X_train_tsf.groupby(col, sort=False)[col].count().sort_values(ascending=False).index)[
                    :dim_cat_threshold
                ]
                for val in values_cat:
                    X_train_tsf[col + "_" + str(val)] = (X_train_tsf[col] == val).astype("int")
                X_train_tsf = X_train_tsf.drop(columns=col)
                cats_feat.remove(col)
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse=False), cats_feat),
            ],
            remainder="passthrough",
        )
        preprocessor.fit(X_train_tsf)
        feat_names = preprocessor.get_feature_names_out()
        feat_names = [re.sub(r"((remainder)|(cat))__", "", x) for x in feat_names]
        X_train_tsf = pd.DataFrame(preprocessor.transform(X_train_tsf), columns=feat_names)
        categorical_shap_ohe = True

    else:
        X_train_tsf[X_train_tsf.select_dtypes(["object"]).columns] = X_train_tsf.select_dtypes(["object"]).apply(
            lambda x: x.astype("category")
        )

    CVSel_algo.fit(X_train_tsf, y_train)

    model = CVSel_algo.best_estimator_

    # Get AUC
    train_model_score = roc_auc_score(y_train, CVSel_algo.predict_proba(X_train_tsf)[:, 1])
    valid_model_score = CVSel_algo.best_score_

    # Get Shap
    shap_importance = get_Shap(X_train_tsf, model, categorical_shap_ohe, categorical_feature, y_train=y_train)

    return shap_importance, model, train_model_score, valid_model_score


def get_Shap_R2(X_train, y_train, CVSel_algo, categorical_feature=None, dim_cat_threshold=10):
    """Get the R squared of the model and Features' Shapley Value.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        y_train (pd.Series): target set.
        CVSel_algo: class that include the regressor, grid search and detail of CV selection.
        categorical_feature (list, optional): list of categorical feature to be preprocessed. Defaults to None.
        dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (pd.DataFrame, classifier, float, float): Shap DataFrame, Best Classifier, Train and Valid R2.

    """
    if categorical_feature is None:
        categorical_feature = []

    # Estimate
    categorical_shap_ohe = False
    X_train_tsf = X_train.copy()
    if len(categorical_feature) > 0:
        # Categorical Preprocessing Hot-One-Encoder
        cats_feat = categorical_feature.copy()
        for col in cats_feat:
            if X_train_tsf[col].nunique() > dim_cat_threshold:
                values_cat = list(X_train_tsf.groupby(col, sort=False)[col].count().sort_values(ascending=False).index)[
                    :dim_cat_threshold
                ]
                for val in values_cat:
                    X_train_tsf[col + "_" + str(val)] = (X_train_tsf[col] == val).astype("int")
                X_train_tsf = X_train_tsf.drop(columns=col)
                cats_feat.remove(col)
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse=False), cats_feat),
            ],
            remainder="passthrough",
        )
        preprocessor.fit(X_train_tsf)
        feat_names = preprocessor.get_feature_names_out()
        feat_names = [re.sub(r"((remainder)|(cat))__", "", x) for x in feat_names]
        X_train_tsf = pd.DataFrame(preprocessor.transform(X_train_tsf), columns=feat_names)
        categorical_shap_ohe = True

    else:
        X_train_tsf[X_train_tsf.select_dtypes(["object"]).columns] = X_train_tsf.select_dtypes(["object"]).apply(
            lambda x: x.astype("category")
        )

    CVSel_algo.fit(X_train_tsf, y_train)

    model = CVSel_algo.best_estimator_

    # Get R2
    train_model_score = r2_score(y_train, CVSel_algo.predict(X_train_tsf))
    valid_model_score = CVSel_algo.best_score_

    # Get Shap
    shap_importance = get_Shap(X_train_tsf, model, categorical_shap_ohe, categorical_feature, y_train=y_train)

    return shap_importance, model, train_model_score, valid_model_score


def get_Shap_BalAcc(X_train, y_train, CVSel_algo, categorical_feature=None, dim_cat_threshold=10):
    """Get the Balanced Accuracy of the model and Features' Shapley Value.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        y_train (pd.Series): target set.
        CVSel_algo: class that include the regressor, grid search and detail of CV selection.
        categorical_feature (list, optional): list of categorical feature to be preprocessed. Defaults to [].
        dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
            Defaults to 10.
    Returns:
        (pd.DataFrame, classifier, float, float): Shap DataFrame, Best Classifier, Train and Valid Balanced accuracy.

    """
    if categorical_feature is None:
        categorical_feature = []

    # Estimate
    categorical_shap_ohe = False
    X_train_tsf = X_train.copy()
    if len(categorical_feature) > 0:
        # Categorical Preprocessing Hot-One-Encoder
        cats_feat = categorical_feature.copy()
        for col in cats_feat:
            if X_train_tsf[col].nunique() > dim_cat_threshold:
                values_cat = list(X_train_tsf.groupby(col, sort=False)[col].count().sort_values(ascending=False).index)[
                    :dim_cat_threshold
                ]
                for val in values_cat:
                    X_train_tsf[col + "_" + str(val)] = (X_train_tsf[col] == val).astype("int")
                X_train_tsf = X_train_tsf.drop(columns=col)
                cats_feat.remove(col)
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse=False), cats_feat),
            ],
            remainder="passthrough",
        )
        preprocessor.fit(X_train_tsf)
        feat_names = preprocessor.get_feature_names_out()
        feat_names = [re.sub(r"((remainder)|(cat))__", "", x) for x in feat_names]
        X_train_tsf = pd.DataFrame(preprocessor.transform(X_train_tsf), columns=feat_names)
        categorical_shap_ohe = True

    else:
        X_train_tsf[X_train_tsf.select_dtypes(["object"]).columns] = X_train_tsf.select_dtypes(["object"]).apply(
            lambda x: x.astype("category")
        )

    CVSel_algo.fit(X_train_tsf, y_train)

    model = CVSel_algo.best_estimator_
    # Get Balanced Accuracy
    train_model_score = balanced_accuracy_score(y_train, CVSel_algo.predict(X_train_tsf))
    valid_model_score = CVSel_algo.best_score_

    # Get Shap
    shap_importance = get_Shap(X_train_tsf, model, categorical_shap_ohe, categorical_feature, y_train=y_train)

    return shap_importance, model, train_model_score, valid_model_score


def get_new_X(X_train, shap_importance, step_size=0.1, min_n_feat_step=5, final_n_feature=1):
    """Determines the reduced DataFrame excluding the shap-useless features.

    Args:
        X_train (pd.DataFrame): Feature dataset.
        shap_importance(pd.DataFrame): Shap Value DataFrame.
        step_size (int or float, optional): determines how many features to remove at each step.
            Fixed int or percentage of total features. Defaults to 0.1.
        min_n_feat_step (int, optional): min number of feature to remove at each step. Defaults to 5.
        final_n_feature (int, optional): number of features of the last model. Defaults to 1.

    Return:
    (pd.DataFrame, list): Feature Dataset excluding the useless ones, list of removed features.
    """
    # Determine feat to remove
    n_feat = X_train.shape[1]
    if 0 < step_size < 1:
        n_feat_to_remove = np.floor(n_feat * step_size).astype("int")
    elif step_size >= 1 and step_size < step_size:
        n_feat_to_remove = step_size.astype("int")
    else:
        n_feat_to_remove = n_feat - 1

    n_feat_to_remove = min(n_feat - final_n_feature, max(n_feat_to_remove, min_n_feat_step))

    feat_to_remove = list(shap_importance.iloc[0:n_feat_to_remove, 0])
    X_train_red = remove_features(X_train, feat_to_remove)

    return X_train_red, feat_to_remove
