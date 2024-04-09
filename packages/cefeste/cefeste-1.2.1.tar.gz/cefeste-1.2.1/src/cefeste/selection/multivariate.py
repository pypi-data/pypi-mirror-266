# Correlation and VIF
import pandas as pd
import math
import numpy as np
import scipy.stats as stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from random import seed, randint
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

from itertools import combinations
from tqdm import tqdm
import sys
from cefeste.utils import get_numerical_features, get_categorical_features, convert_Int_dataframe
import logging

logging.basicConfig(level=logging.INFO)


# @time_step
def find_correlated_features(
    df,
    correlation_threshold=0.95,
    feat_to_check=None,
    selection_rule="random",
    random_state=42,
    feat_univ_perf=pd.DataFrame(),
    verbose=False,
    return_selection_history=False,
    return_avg_corr=False,
):
    """Retrieve the list of highly correlated features.

    This function evaluates:
    - Spearman correlation for numerical features;
    - Cramers'V for categorical features;
    - R2 for mixed correlation

    Args:
    df (pd.DataFrame): Dataset under analysis
    correlation_threshold (float): correlation limit to define a couple of features highly correlated
    feat_to_check (list, opt.): list of features to analyse. If empty all are used
    selection_rule(str): 'random' or 'univ_perf'. The rule to define which feature in the couple to keep.
        If 'random' it is randomly chosen and the 'random_state' can be defined.
        If 'univ_perf' than the feature with the highest univariate performance is used.
            In this case 'feat_univ_perf' has to be passed as argument.
    random_state(int, opt.): random seed for 'random' selection_rule
    feat_univ_perf (pd.DataFrame): Dataset containing the features' univariate performance
    verbose (bool): If true print a log of the selection chosen.
    return_selection_history (bool): If True return the Dataset containing the selection choices, otherwise return None.
    return_avg_correlation (bool): If True return an additional Dataset containing the average correlations.

    Returns:
        list: list of features highly correlated.
        pd.Dataframe (or None): Dataset containing the selection choices.
        pd.Dataframe (opt.): Dataset containing the average correlations
    """
    if selection_rule not in ("random", "univ_perf"):
        raise ValueError("selection_rule must be either 'random' or 'univ_perf'")
    if feat_to_check is None:
        feat_to_check = df.columns
    if return_selection_history:
        history_list = [pd.DataFrame()] * 3

    nums = get_numerical_features(df[feat_to_check])
    cats = get_categorical_features(df[feat_to_check])
    len_n = len(nums)
    len_c = len(cats)

    # Aggiungi roba in questo range per printare anche "removing num features", "removing cat feature".. ecc ecc
    pb = tqdm(
        range(int(len_n * (len_n - 1) * 0.5 + len_c * (len_c - 1) * 0.5 + len_n * len_c + 3)),
        file=sys.stdout,
        desc="Calculating correlations between numerical features",
        ncols=100,
        leave=True,
    )
    # For Numerical Feature calculate Spearman and take the absolute values
    if len_n > 1:
        corrs = df[nums].corr(method="spearman").abs().stack().reset_index()
        pb.update(len_n * (len_n - 1) * 0.5)
        pb.set_description("Removing numerical features", refresh=True)
        # Sort correlations
        corrs.columns = ["feat1", "feat2", "value"]
        corrs = corrs.loc[corrs["feat1"] != corrs["feat2"]].sort_values("value", ascending=False)

        # Remove highly correlated couples
        residual_corrs_num, num_history = remove_correlated(
            corrs,
            correlation_threshold=correlation_threshold,
            selection_rule=selection_rule,
            random_state=random_state,
            feat_univ_perf=feat_univ_perf,
            return_selection_history=return_selection_history,
            verbose=verbose,
            prog_bar=pb,
        )
        if return_selection_history:
            history_list[0] = num_history.assign(corr_type="numerical")
        # Finalize the lists to keep/drop
        num_keep_list = residual_corrs_num["feat1"].drop_duplicates().tolist()
        num_drop_list = list(set(nums) - set(num_keep_list))
        pb.update(1)
        if verbose:
            pb.write(f"List of numerical features dropped: {num_drop_list}")
    else:
        residual_corrs_num = pd.DataFrame()
        num_keep_list = nums
        num_drop_list = []
        pb.update(1)
    # For Categorical Features calculate Cramers'V
    if len_c > 1:
        pb.set_description("Calculating correlations between categorical features", refresh=True)
        corrs = pd.DataFrame()
        for var1, var2 in combinations(cats, 2):
            corrs = pd.concat(
                [
                    corrs,
                    pd.DataFrame(
                        {
                            "feat1": [var1],
                            "feat2": [var2],
                            "value": Cramers_pair_correlation(var1, var2, df, False),
                        }
                    ),
                ]
            )
            pb.update(1)
        pb.set_description("Removing categorical features", refresh=True)
        corrs = corrs.sort_values("value", ascending=False)

        # Remove highly correlated couples
        residual_corrs_cat, cat_history = remove_correlated(
            corrs,
            correlation_threshold=correlation_threshold,
            selection_rule=selection_rule,
            random_state=random_state,
            feat_univ_perf=feat_univ_perf,
            return_selection_history=return_selection_history,
            verbose=verbose,
            prog_bar=pb,
        )
        if return_selection_history:
            history_list[1] = cat_history.assign(corr_type="categorical")
        # Finalize the lists to keep/drops
        cat_keep_list = pd.concat([residual_corrs_cat["feat1"], residual_corrs_cat["feat2"]]).drop_duplicates().tolist()
        cat_drop_list = list(set(cats) - set(cat_keep_list))
        pb.update(1)
        if verbose:
            pb.write(f"List of categorical features dropped: {cat_drop_list}")
    else:
        pb.update(1)
        residual_corrs_cat = pd.DataFrame()
        cat_keep_list = cats
        cat_drop_list = []

    # Check mixed correlation
    nums = get_numerical_features(df[num_keep_list])
    cats = get_categorical_features(df[cat_keep_list])
    if (len(nums) > 0) & (len(cats) > 0):
        uu = (len_n * len_c) / (len(nums) * len(cats))
        pb.set_description("Calculating correlations mixed features", refresh=True)
        corrs = pd.DataFrame()
        for var1 in nums:
            for var2 in cats:
                corrs = pd.concat(
                    [
                        corrs,
                        pd.DataFrame(
                            {
                                "feat1": [var1],
                                "feat2": [var2],
                                "value": numerical_categorical_correlation(
                                    df[var2].astype("object").fillna("Missing"), df[var1].fillna(0)
                                ),
                            }
                        ),
                    ]
                )
                pb.update(uu)
        pb.set_description("Removing mixed features", refresh=True)
        corrs = corrs.sort_values("value", ascending=False)
        # Remove highly correlated couples
        residual_corrs_mix, mix_history = remove_correlated(
            corrs,
            correlation_threshold=correlation_threshold,
            selection_rule=selection_rule,
            random_state=random_state,
            feat_univ_perf=feat_univ_perf,
            return_selection_history=return_selection_history,
            verbose=verbose,
            prog_bar=pb,
        )
        if return_selection_history:
            history_list[2] = mix_history.assign(corr_type="mixed")
        # Finalize the lists to keep/drop
        mixed_keep_list = (
            pd.concat([residual_corrs_mix["feat1"], residual_corrs_mix["feat2"]]).drop_duplicates().tolist()
        )
        mixed_drop_list = list(set(nums + cats) - set(mixed_keep_list))
        pb.set_description("Completed find_correlated_features", refresh=True)
        pb.update(1)
        if verbose:
            pb.write(f"List of mixed features dropped: {mixed_drop_list}")
    else:
        pb.set_description("Completed find_correlated_features", refresh=True)
        pb.update(len_n * len_c + 1)
        residual_corrs_mix = pd.DataFrame()
        mixed_drop_list = []

    if return_selection_history:
        selection_history = pd.concat(history_list).reset_index(drop=True)
    else:
        selection_history = None

    if return_avg_corr:
        corr_avg = (
            pd.concat(
                [
                    residual_corrs_num,
                    residual_corrs_cat,
                    residual_corrs_cat.rename(columns={"feat1": "feat2", "feat2": "feat1"}),
                    residual_corrs_mix,
                    residual_corrs_mix.rename(columns={"feat1": "feat2", "feat2": "feat1"}),
                ]
            )
            .groupby("feat1")["value"]
            .mean()
        )

        return num_drop_list + cat_drop_list + mixed_drop_list, selection_history, corr_avg

    else:
        return num_drop_list + cat_drop_list + mixed_drop_list, selection_history


def Cramers_V(x, y, bias_correction=True):
    """Implementation of the corrected Cramer's V statistic.

    It measure the association between two nominal variables.
    It provides a value between 0 and 1 as output.
    Because Cramer's V can be biased, a bias correction is computed as default.
    The original value can be obtained by setting the bias_correction to False.
    Args:
        x (pd.Series): nominal variable.
        y (pd.Series): nominal variable.
        bias_correction (boolean): flag to compte the corrected Cramer's V.
    Returns:
        float: correlation between the two nominal variables.
    """
    confusion_matrix = pd.crosstab(x, y)
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()

    phi2 = chi2 / n

    r, k = confusion_matrix.shape

    CramersV = np.sqrt(phi2 / min((k - 1), (r - 1)))

    if bias_correction:
        phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
        rcorr = r - ((r - 1) ** 2) / (n - 1)
        kcorr = k - ((k - 1) ** 2) / (n - 1)
        CramersV = np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))

    return CramersV


def Cramers_pair_correlation(feature_1, feature_2, df, verbose):
    """Call (corrected) Cramers V for a pair of nominal features.

    Args:
        feature_1 (string): label of the first feature.
        feature_2 (string): label of the second feature.
        df (pd.DataFrame): feature matrix.
        verbose (boolean): flag to print more output.

    Returns:
        float: correlation between the tow features
    """
    pair_df = df[[feature_1, feature_2]].dropna()

    try:
        correlation = Cramers_V(pair_df[feature_1], pair_df[feature_2])

    # If the correlation throws an error assume correlation is 0 except if
    # the two features are the same. Then it should be 1.
    except Exception:
        correlation = 0
        if feature_1 == feature_2:
            correlation = 1

    if verbose:
        logging.info(feature_1, feature_2, correlation)

    return correlation


def numerical_categorical_correlation(categ, numerical):
    """Compute the correlation between numerical and categorical features.

    It uses a regression of the OHE categorical variable on the numerical variable.
    Please note this is a proxy.
    Args:
        categ (pd.Series or np.array): Values for the categorical variable.
        numerical (pd.Series or np.array): Values for the numerical variable.

    Returns:
        float with the R-square value.
    """
    dummies = pd.get_dummies(pd.DataFrame(categ))

    linear_regression = LinearRegression().fit(dummies, numerical)

    sqrt_r2 = math.sqrt(max(r2_score(numerical, linear_regression.predict(dummies)), 0))

    return sqrt_r2


def remove_correlated(
    flat_corr_db,
    correlation_threshold=0.95,
    selection_rule="random",
    random_state=42,
    feat_univ_perf=pd.DataFrame(),
    return_selection_history=False,
    selection_history=None,
    verbose=False,
    prog_bar=None,
):
    """Identify and remove from the stacked correlation matrix the highly correlated feature.

    Args:
        flat_corr_db: stacked correlation matrix with columns: 'feat1', 'feat2', 'value'
        correlation_threshold (float): correlation limit to define a couple of features highly correlated
        feat_to_check (list, opt.): list of features to analyse. If empty all are used
        selection_rule(str): 'random' or 'univ_perf'. The rule to define which feature in the couple to keep.
            If 'random' it is randomly chosen and the 'random_state' can be defined.
            If 'univ_perf' than the feature with the highest univariate performance is used.
                'feat_univ_perf' has to be passed as argument.
        random_state(int, opt.): random seed for 'random' selection_rule
        feat_univ_perf (pd.DataFrame): Dataset containing the features' univariate performance
        verbose (bool): If true print a log of the selection chosen.

    Returns:
        pd.DataFrame with the residual correlations
    """
    if (return_selection_history) & (selection_history is None):
        selection_history = pd.DataFrame()
    if flat_corr_db.loc[lambda x: x.value > correlation_threshold].shape[0] > 0:
        if verbose:
            if prog_bar is None:
                logging.info(
                    f"The features correlated are {[flat_corr_db.iloc[0, 0], flat_corr_db.iloc[0, 1]]}, with a correlation of {flat_corr_db.iloc[0, 2]}."
                )
            else:
                prog_bar.write(
                    f"The features correlated are {[flat_corr_db.iloc[0, 0], flat_corr_db.iloc[0, 1]]}, with a correlation of {flat_corr_db.iloc[0, 2]}."
                )

        if selection_rule == "random":
            seed(random_state)
            feat_to_drop = flat_corr_db.iloc[0, randint(0, 1)]
        else:
            perf1 = float(feat_univ_perf.loc[feat_univ_perf["name"] == flat_corr_db.iloc[0, 0]]["perf"])
            perf2 = float(feat_univ_perf.loc[feat_univ_perf["name"] == flat_corr_db.iloc[0, 1]]["perf"])
            if perf1 < perf2:
                feat_to_drop = flat_corr_db.iloc[0, 0]
            else:
                feat_to_drop = flat_corr_db.iloc[0, 1]
        # here i update selection history
        if return_selection_history:
            selection_history = pd.concat(
                [
                    selection_history,
                    pd.DataFrame(
                        {
                            "feat1": flat_corr_db.iloc[0, 0],
                            "feat2": flat_corr_db.iloc[0, 1],
                            "corr": flat_corr_db.iloc[0, 2],
                            "feat_dropped": feat_to_drop,
                        },
                        index=[0],
                    ),
                ]
            )
        if verbose:
            if prog_bar is None:
                logging.info(f"The feature removed is: {feat_to_drop}")
            else:
                prog_bar.write(f"The feature removed is: {feat_to_drop}")
        # if after having dropped the feature to drop, the residuals corrs dataframe results empty, we replace the feat to drop with the other feature in order to keep trace of the remaining features
        if (
            flat_corr_db.loc[(flat_corr_db["feat1"] != feat_to_drop) & (flat_corr_db["feat2"] != feat_to_drop)].shape[0] == 0
        ):
            flat_corr_db["feat2"] = flat_corr_db.apply(
                lambda row: row["feat1"] if row["feat2"] == feat_to_drop else row["feat2"], axis=1
            )
            flat_corr_db["feat1"] = flat_corr_db.apply(
                lambda row: row["feat2"] if row["feat1"] == feat_to_drop else row["feat1"], axis=1
            )
            flat_corr_db["value"] = 1
            return flat_corr_db, selection_history
        else:
            flat_corr_db = flat_corr_db.loc[
                (flat_corr_db["feat1"] != feat_to_drop) & (flat_corr_db["feat2"] != feat_to_drop)
            ]
        flat_corr_db, selection_history = remove_correlated(
            flat_corr_db,
            selection_rule=selection_rule,
            correlation_threshold=correlation_threshold,
            random_state=random_state,
            feat_univ_perf=feat_univ_perf,
            return_selection_history=return_selection_history,
            selection_history=selection_history,
            verbose=verbose,
            prog_bar=prog_bar,
        )

    return flat_corr_db, selection_history


def find_collinear_feature(df, vif_threshold=5, feat_to_check=None, verbose=True):
    """Find the list of feature with a VIF higher than a threshold in order to avoid multi collinearity.

    Args:
        df (pd.DataFrame): Dataframe on which check the VIF
        vif_threshold (int): vif maximum level
        feat_to_check (list, opt.): list of features to analyse. If empty all are used.
        verbose (bool): If true print a log of the elimination process.

    Returns:
        list: feature that causes multi-collinearity to be dropped

    """
    if feat_to_check is None:
        feat_to_check = df.columns

    nums = get_numerical_features(df[feat_to_check])
    db = df[nums]
    pb = tqdm(range(len(nums)), file=sys.stdout, desc="Removing collinear features", ncols=100, leave=True)
    feat_to_keep = vif_ok_cycle(db, vif_threshold=vif_threshold, verbose=verbose, prog_bar=pb)
    pb.set_description("Completed find_collinear_features", refresh=True)
    pb.update(len(feat_to_keep))
    feat_to_drop = list(set(nums) - set(feat_to_keep))
    return feat_to_drop


def vif_ok_cycle(db, vif_threshold=5, verbose=True, prog_bar=None):
    """Cycle for recursive vif check and feature elimination.

    Args:
        db (pd.DataFrame): Dataframe on which check the VIF
        vif_threshold (int): vif maximum level
        verbose (bool): If true print a log of the elimination process.

    Returns:
        list: feature that ha to be kept
    """
    tmp = add_constant(db)
    results = pd.Series(
        [variance_inflation_factor(convert_Int_dataframe(tmp.fillna(0)).values, i) for i in range(tmp.shape[1])],
        index=tmp.columns,
    )
    results = results[results.index != "const"]

    feat_to_keep = list(results.loc[results < vif_threshold].index)

    if results.max() > vif_threshold:
        feat_to_drop = results.idxmax()
        db = db.drop(columns=feat_to_drop)
        if prog_bar is not None:
            prog_bar.update(1)
        if verbose & (prog_bar is not None):
            prog_bar.write(f"The feature {feat_to_drop} has a VIF of {results.max()}. It has been removed")
        keeps = vif_ok_cycle(db, vif_threshold=vif_threshold, verbose=verbose, prog_bar=prog_bar)
        feat_to_keep = list(set(keeps).union(set(feat_to_keep)))
    return feat_to_keep


# @time_step
def find_collinear_feature_optimized(
    df, vif_threshold=5, feat_to_check=None, verbose=True, optimize=False, optim_Series=None, optim_value_ascending=True
):
    """Find the list of feature with a VIF higher than a threshold in order to avoid multi collinearity.

    Instead of perform the classical analysis, this function is a time-saver if used with optimize parameters.
    Wehn optimize is used, the features are checked in a defined order.

    Args:
        df (pd.DataFrame): Dataframe on which check the VIF
        vif_threshold (int): vif maximum level
        feat_to_check (list, opt.): list of features to analyse. If empty all are used.
        verbose (bool): If true print a log of the elimination process.
        optimize (bool): If true, it requires optim_series and perform VIF analysis in determined order.
        optim_Series (pd.Series): Series that express a value for each feature to be checked
        optim_value_ascending (bool): If True the first feature to be checked is the one with the lowest value.
            Otherwise, the highest one is the first.

    Returns:
        list: feature that causes multi-collinearity to be dropped

    """
    if optim_Series is None:
        optim_Series = pd.Series()

    if optimize:
        if feat_to_check is None:
            feat_to_check = df.columns

        nums = get_numerical_features(df[feat_to_check])
        index_ok = list(set(optim_Series.index) & set(nums))
        optim_Series_reduced = optim_Series[index_ok]
        db = df[nums]

        db_nums = add_constant(db)

        col_order = list(optim_Series_reduced.sort_values(ascending=optim_value_ascending).index)
        feat_to_drop = recursive_vif(db_nums, col_order, vif_threshold=vif_threshold, verbose=verbose)

    else:
        feat_to_drop = find_collinear_feature(
            df, vif_threshold=vif_threshold, feat_to_check=feat_to_check, verbose=verbose
        )

    return feat_to_drop


def recursive_vif(
    df,
    col_order,
    vif_threshold=5,
    verbose=True,
):
    """Perform VIF check recursively, one feature after the other in the predefined order.

    Args:
        df (pd.DataFrame): Dataframe on which check the VIF
        col_order (list): list of feature ordered from the first to be cheked to the latest one.
        vif_threshold (int): vif maximum level
        verbose (bool): If true print a log of the elimination process.


    Returns:
        list: feature that causes multi-collinearity to be dropped
    """
    tmp = df.copy()

    pb = tqdm(col_order, file=sys.stdout, desc="Removing collinear features", ncols=100, leave=True)
    for ix, col in enumerate(pb):
        vif_col = variance_inflation_factor(convert_Int_dataframe(tmp.fillna(0)).values, tmp.columns.get_loc(col))
        if vif_col > vif_threshold:
            tmp = tmp.drop(columns=[col])
            if verbose:
                pb.write(f"The feature {col} has a VIF of {vif_col}. It has been removed")
        if ix == len(col_order) - 1:
            pb.set_description("Completed find_collinear_feature_optimized", refresh=True)

    feat_to_drop = list(set(df.columns) - set(tmp.columns))
    return feat_to_drop
