# Univariate filters
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
from cefeste.utils import get_categorical_features, time_step


@time_step
def find_constant_features(df, feat_to_check=None):
    """Retrieve the list of features that are constant.

    Args:
        df (pd.DataFrame): DataFrame to be checked
        feat_to_check (list): list of features to be checked
    Returns:
        list: list of constant features
    """
    if feat_to_check is None:
        feat_to_check = []

    if len(feat_to_check) == 0:
        feat_to_check = df.columns

    feat_to_remove = df[feat_to_check].loc[:, lambda db: (db.nunique() == 1)].columns.tolist()

    return feat_to_remove


@time_step
def find_low_nvalues_features(df, min_unique_val=2, feat_to_check=None):
    """Retrieve the list of features that have a number of distinct values lower than the minimum.

    If min_unique_val = 2 the function gets the same result as find_constant_features.

    Args:
        df (pd.DataFrame): DataFrame to be checked
        min_unique_val (int): minimum number of distinct values
        feat_to_check (list): list of features to be checked
    Returns:
        list: list of constant features
    """
    if feat_to_check is None:
        feat_to_check = []

    if len(feat_to_check) == 0:
        feat_to_check = df.columns
    feat_to_remove = df[feat_to_check].loc[:, lambda db: (db.nunique() < min_unique_val)].columns.tolist()

    return feat_to_remove


@time_step
def find_missing_features(df, max_pct_missing=0.9, feat_to_check=None):
    """Retrieve the list of features that have missings percentage higher than threshold.

    Args:
        df (pd.DataFrame): DataFrame to be checked
        max_pct_missing (float): threshold of missings percentage acceptable
        feat_to_check (list): list of features to be checked
    Returns:
        list: list of constant features
    """
    if feat_to_check is None:
        feat_to_check = []

    if len(feat_to_check) == 0:
        feat_to_check = df.columns

    feat_to_remove = (
        df[feat_to_check].loc[:, lambda db: (db.isna().sum(axis=0) / db.shape[0] > max_pct_missing)].columns.tolist()
    )

    return feat_to_remove


def find_high_topcat_features(df, max_pct_mfv=0.95, feat_to_check=None):
    """Retrieve the list of features that are equals to a unique value for too many observations.

    Args:
        df (pd.DataFrame): DataFrame to be checked
        max_pct_mfv (float): Maximum percentage of the Most Frequent Value acceptable
        feat_to_check (list): list of features to be checked
    Returns:
        list: list of constant features
    """
    if feat_to_check is None:
        feat_to_check = []

    if len(feat_to_check) == 0:
        feat_to_check = df.columns
    feat_to_check_pb = tqdm(feat_to_check, file=sys.stdout, desc="Performing find_high_topcat_features", ncols=100)
    feat_to_remove = []
    for ix, col in enumerate(feat_to_check_pb):
        if df.loc[df[col] == df[col].mode()[0]].shape[0] / df.shape[0] > max_pct_mfv:
            feat_to_remove.append(col)
        if ix == len(feat_to_check) - 1:
            feat_to_check_pb.set_description("Completed find_high_topcat_features", refresh=True)

    return feat_to_remove


def find_unstable_psi_features(
    base_df, compare_df, max_psi=0.2, psi_nbins=20, psi_bin_min_pct=0.02, feat_to_check=None
):
    """Retrieve the list of features that are unstable between sets (usually train and test).

    Args:
        base_df (pd.DataFrame): reference dataset, usually the train set.
        compare_df (pd.DataFrame): comparison dataset, usually the test set.
        max_psi (float): maximum psi acceptable
        psi_nbins (int): number of bins into which the features will be bucketed (maximum) to compute psi
        psi_bin_min_pct (float): minimum percentage of observations per bucket
        feat_to_check (list): list of features to be checked
    Returns:
        list: list of constant features
    """
    if feat_to_check is None:
        feat_to_check = []

    psi_results = retrieve_psis(
        base_df, compare_df, feat_to_check, psi_nbins=psi_nbins, psi_bin_min_pct=psi_bin_min_pct
    )

    feat_to_remove = [x for x, y in psi_results.items() if y > max_psi]

    return feat_to_remove


def retrieve_psis(base_df, compare_df, features, psi_nbins=20, psi_bin_min_pct=0.02):
    """Retrieve psi for all the features.

    Args:
        base_df (pd.DataFrame): reference dataset, usually the train set.
        compare_df (pd.DataFrame): comparison dataset, usually the test set.
        psi_nbins (int): number of bins into which the features will be bucketed (maximum) to compute psi
        psi_bin_min_pct (float): minimum percentage of observations per bucket
        features (list): list of features to be checked
    Returns:
        dict: dictionary reporting for each feature (key) the psi value (value)
    """
    if len(features) == 0:
        features = base_df.columns

    psis = dict()
    features_pb = tqdm(features, file=sys.stdout, desc="Performing find_unstable_psi_features", ncols=100, leave=True)
    for ix, col in enumerate(features_pb):
        if col in get_categorical_features(base_df):
            if base_df[col].dtype == 'category':
                base_df[col] = base_df[col].astype('object').fillna("Missing").astype('category')
                compare_df[col] = compare_df[col].astype('object').fillna("Missing").astype('category')
            else:
                base_df[col] = base_df[col].fillna("Missing")
                compare_df[col] = compare_df[col].fillna("Missing")
            mapper = retrieve_bin_categorical(base_df, col, max_n_bins=psi_nbins)
            mapper = merge_categorical_bins(base_df, col, mapper, bin_min_pct=psi_bin_min_pct)
            base_bin = base_df[col].map(mapper)
            comp_bin = compare_df[col].map(mapper)
        else:
            base_df[col] = base_df[col].fillna(-999999)
            compare_df[col] = compare_df[col].fillna(-999999)
            cuts = retrieve_bin_numerical(base_df, col, max_n_bins=psi_nbins)
            cuts = merge_numerical_bins(base_df, col, cuts, bin_min_pct=psi_bin_min_pct)
            base_bin = pd.cut(base_df[col], cuts, right=True, duplicates="drop")
            comp_bin = pd.cut(compare_df[col].astype("float"), cuts, right=True, duplicates="drop")
        if ix == len(features) - 1:
            features_pb.set_description("Completed find_unstable_psi_features", refresh=True)
        psis[col] = psi_value(base_bin, comp_bin)

    return psis


def retrieve_bin_categorical(df, feat, max_n_bins=20):
    """Retrieve the bucket for a categorical feature.

    Args:
        df (pd.DataFrame): DataFrame to be used
        feat (str): feature to be bucketed
        max_n_bins (int): number of bins into which the features will be bucketed (maximum) to compute psi
    Returns:
        dict: mapper to be used to bucket the feature feat
    """
    if df[feat].nunique() > max_n_bins:
        freqs = df[feat].value_counts(ascending=False)
        mapper_1_1 = {x: x for x in freqs.index[: max_n_bins - 1]}
        mapper_other = {x: "_other_" for x in freqs.index[max_n_bins - 1 :]}
        mapper = {**mapper_1_1, **mapper_other}
    else:
        mapper = {x: x for x in df[feat].unique()}

    return mapper


def merge_categorical_bins(df, feat, mapper, bin_min_pct=0.02):
    """Merge buckets that have low frequency.

    Args:
        df (pd.DataFrame): DataFrame to be used
        feat (str): feature to be bucketed
        mapper (dict): initial mapper to be used to bucket the feature feat
        bin_min_pct (float): minimum percentage of observations per bucket

    Returns:
        dict: mapper to be used to bucket the feature feat
    """
    db = df[[feat]].assign(bin=df[feat].map(mapper))

    freqs = db["bin"].value_counts(ascending=True, normalize=True)

    if freqs.iloc[0] < bin_min_pct:
        update = {x: freqs.index[1] for x, y in mapper.items() if y == freqs.index[0]}
        mapper.update(update)
        mapper = merge_categorical_bins(df, feat, mapper, bin_min_pct)

    return mapper


def retrieve_bin_numerical(df, feat, max_n_bins=20):
    """Retrieve the bucket for a categorical feature.

    Args:
        df (pd.DataFrame): DataFrame to be used
        feat (str): feature to be bucketed
        max_n_bins (int): number of bins into which the features will be bucketed (maximum) to compute psi
    Returns:
        list: the list of cuts to be used in pd.cut
    """
    if df[feat].nunique() > max_n_bins:
        db = df[[feat]].assign(bucket=pd.qcut(df[feat], q=max_n_bins, labels=False, duplicates="drop"))
        cuts = list(db.groupby("bucket")[feat].max())
    else:
        cuts = list(df[feat].unique())

    cuts.sort()
    cuts = [-np.Inf] + cuts
    cuts[-1] = np.Inf

    return cuts


def merge_numerical_bins(df, feat, cuts, bin_min_pct=0.02):
    """Merge buckets that have low frequency.

    Args:
        df (pd.DataFrame): DataFrame to be used
        feat (str): feature to be bucketed
        cuts (list): initial cuts to be used to bucket the feature feat
        bin_min_pct (float): minimum percentage of observations per bucket

    Returns:
        dict: mapper to be used to bucket the feature feat
    """
    db = df[[feat]].assign(bin=pd.cut(df[feat], bins=cuts, labels=False, right=True))
    freqs = db["bin"].value_counts(ascending=True, normalize=True)

    if freqs.iloc[0] < bin_min_pct:
        remove_cut = min(min(cuts[1:]), max(max(cuts[:-1]), freqs.index[0]))
        cuts.remove(remove_cut)
        cuts = merge_numerical_bins(db, feat, cuts, bin_min_pct=bin_min_pct)

    return cuts


def psi_value(ref, new):
    """Retrieve the psi.

    Args:
        ref (pd.Series): series of the features in the base/reference dataset
        new (pd.Series): series of the features in the new/comparison dataset
    Returns:
        float: the psi
    """
    ref_count = pd.DataFrame(ref.value_counts(normalize=True))
    ref_count.columns = ["ref"]
    new_count = pd.DataFrame(new.value_counts(normalize=True))
    new_count.columns = ["new"]

    merged = ref_count.merge(new_count, how="left", left_index=True, right_index=True).fillna(0)
    # merged.clip(lower=0.000001)

    merged["psi"] = (merged["new"] - merged["ref"]) * (np.log((merged["new"] / merged["ref"]) + 1e-9))
    return merged["psi"].sum()
