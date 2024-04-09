from cefeste import FeatureAnalysis
from cefeste.utils import remove_features, get_numerical_features, convert_Int_series
from cefeste.selection.explanatory import find_not_explanatory
from cefeste.selection.multivariate import find_collinear_feature_optimized, find_correlated_features
from cefeste.selection.univariate import (
    find_constant_features,
    find_high_topcat_features,
    find_low_nvalues_features,
    find_missing_features,
    find_unstable_psi_features,
)

import warnings
from itertools import combinations
from functools import reduce

import pandas as pd
from numpy import nan


class FeatureSelection(FeatureAnalysis):
    """Child class of FeatureAnalysis for Feature Selection."""

    def __init__(
        self,
        # DB / Feature Parameters
        db,
        feat_to_check=None,
        target_col=None,
        algo_type="auto",
        sample_col=None,
        sample_train_value=None,
        # Univariate Analysis Parameters
        min_unique_val=3,
        max_pct_missing=0.9,
        max_pct_mfv=0.95,
        max_psi=0.2,
        psi_nbins=20,
        psi_bin_min_pct=0.02,
        # Univariate Explanatory Power Parameters
        explanatory_threshold=0.05,
        # Multivariate Analysis Parameters
        correlation_threshold=0.95,
        selection_rule="random",
        vif_threshold=5,
        collinear_optimize=False,
        return_selection_history=True,
        dim_cat_threshold=10,
        # Generic Parameters
        random_state=42,
        verbose=True,
    ):
        """Feature Selection Class.

        Args:
            db (pd.DataFrame): DataFrame to analyze
            feat_to_check (list, optional): Feature to analyze. If None all are used. Defaults to None.
            target_col (str, optional): Name of the target column. Defaults to None.
            algo_type (str, optional): Type of algo. It should be one of the following:
                'auto', 'regression', 'multiclass', 'classification', 'unsupervised'. Defaults to "auto".
            sample_col (str, optional): Name of the columns that indicates the samples (train, test). Defaults to None.
            sample_train_value (str, optional): Value of the sample column that indicates the train set. Defaults to None.
            min_unique_val (int, optional): Minimum number of unique value to be used by find_low_values. Defaults to 3.
            max_pct_missing (float, optional): Max percentage of missing to be used by find_missing filter. Defaults to 0.9.
            max_pct_mfv (float, optional): Max percentage of the most frequent value. Defaults to 0.95.
            max_psi (float, optional): Max PSI. Defaults to 0.2.
            psi_nbins (int, optional): Number of bins to caluclate PSI. Defaults to 20.
            psi_bin_min_pct (float, optional): Min percentage of observation per Bin when calculating psi. Defaults to 0.02.
            explanatory_threshold (float, optional): Threshold for explanatory power. Defaults to 0.05.
            correlation_threshold (float, optional): Correlation threshold. Defaults to 0.95.
            selection_rule (str, optional): Selection rule for correlation. Defaults to "random".
            vif_threshold (int, optional): VIF Threshold. Defaults to 5.
            collinear_optimize (bool, optional): Flag for using the optimized version of collinear check. Defaults to False.
            dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
                Defaults to 10.
            random_state (int, optional): random state. Defaults to 42.
            verbose (bool, optional): Boolean to print more information. Defaults to True.

        """
        super().__init__(db, feat_to_check)
        self.feat_to_check = list(set(self.feat_to_check) - set([target_col, sample_col]))
        # Target check
        if (target_col in db.columns) | (target_col is None):
            self.target_col = target_col
        else:
            raise ValueError(f"{target_col} not in DataFrame")

        # Check the target var and set the algo type
        if algo_type not in ["auto", "regression", "classification", "multiclass", "unsupervised"]:
            raise ValueError(
                f"{algo_type} is not a valid algo_type. It should be one of the following:\n ['auto', 'regression', 'classification', 'multiclass', 'unsupervised']"
            )

        if target_col is not None:
            vals = db[target_col].nunique()
            if vals == 1:
                raise ValueError(f"The target column {target_col} selected is constant")
            elif algo_type != "auto":
                self.algo_type = algo_type
            elif vals == 2:
                self.algo_type = "classification"
            elif vals < 11:
                self.algo_type = "multiclass"
            else:
                self.algo_type = "regression"
        else:
            self.algo_type = "unsupervised"

        # Sample column check
        if (sample_col in db.columns) | (sample_col is None):
            self.sample_col = sample_col
        else:
            raise ValueError(f"{sample_col} not in DataFrame")
        # Save the list of samples in db
        if sample_col is not None:
            self._sample_list = db[sample_col].unique()
            self._n_sample = db[sample_col].nunique()
        else:
            self._sample_list = []
            self._n_sample = 0
        # Sample Train value
        if (sample_train_value is not None) & (sample_train_value not in self._sample_list):
            raise ValueError(
                f"The value {sample_train_value} set for parameter sample_train_value is not in {sample_col}."
            )
        else:
            self.sample_train_value = sample_train_value

        # Parameters
        self.min_unique_val = min_unique_val
        self.max_pct_missing = max_pct_missing
        self.max_pct_mfv = max_pct_mfv
        self.max_psi = max_psi
        self.psi_nbins = psi_nbins
        self.psi_bin_min_pct = psi_bin_min_pct
        self.explanatory_threshold = explanatory_threshold
        self.correlation_threshold = correlation_threshold
        self.selection_rule = selection_rule
        self.vif_threshold = vif_threshold
        self.collinear_optimize = collinear_optimize
        self.random_state = random_state
        self.verbose = verbose
        self.return_selection_history = return_selection_history
        self.dim_cat_threshold = dim_cat_threshold

        # Initialize the attributes as empty lists/dataframes
        self._constant_features = []
        self._missing_features = []
        self._highly_concentrated_features = []
        self._low_values_features = []
        self._unstable_features = []
        self._unexplanatory_features = []
        self._correlated_features = []
        self._collinear_features = []
        self._selected_features = self.feat_to_check
        self._filtered_out_features = []
        self._funnel_df = pd.DataFrame(
            {
                "Step_Description": "Initial feat to check",
                "Col_Removed": 0,
                "Col_Kept": len(self.feat_to_check),
                "Params": nan,
            },
            index=[0],
        ).rename_axis("Step_Number")

        # Initialize the attributes as False
        self.filter_constant = False
        self.filter_missing = False
        self.filter_missing = False
        self.filter_highly_concentrated = False
        self.filter_low_values = False
        self.filter_unstable = False
        self.filter_unexplanatory = False
        self.filter_correlated = False
        self.filter_collinear = False

        self._perf_db = pd.DataFrame()
        self._selection_history = pd.DataFrame()

    def run(
        self,
        filter_constant=True,
        filter_missing=True,
        filter_highly_concentrated=True,
        filter_low_values=False,
        filter_unstable=True,
        filter_unexplanatory=True,
        filter_correlated=True,
        filter_collinear=True,
        **kwargs,
    ):
        """Perform the filtering.

        Args:
            filter_constant (bool, optional): _description_. Defaults to True.
            filter_missing (bool, optional): _description_. Defaults to True.
            filter_highly_concentrated (bool, optional): _description_. Defaults to True.
            filter_low_values (bool, optional): _description_. Defaults to False.
            filter_unstable (bool, optional): _description_. Defaults to True.
            filter_unexplanatory (bool, optional): _description_. Defaults to True.
            filter_correlated (bool, optional): _description_. Defaults to True.
            filter_collinear (bool, optional): _description_. Defaults to True.

        Returns:
            pd.DataFrame: filtered db
        """
        self.set_params(exceptions="feat_to_check", **kwargs)
        # for k, v in kwargs.items():
        #    self.__dict__[k] = v

        db = self.db
        db.reset_index(inplace=True, drop=True)

        if self.sample_col is not None:
            df, sample_series = self.db.drop(columns=self.sample_col), self.db[self.sample_col]
        else:
            df = db

        if self.target_col is not None:
            X, y = df.drop(columns=self.target_col), df[self.target_col]
        else:
            X = df
        X = X[self._selected_features]
        # self._X_original = X

        if self.sample_train_value is not None:
            X_train = X.loc[sample_series == self.sample_train_value]
        else:
            X_train = X

        if filter_constant:
            _constant_features = find_constant_features(
                X_train,
            )
            self.__union__("_constant_features", _constant_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Constant",
                    "Col_Removed": len(_constant_features),
                    "Col_Kept": len(X_train.columns) - len(_constant_features),
                    "Params": nan,
                }
            )
            X_train = remove_features(X_train, _constant_features)

        if filter_missing:
            _missing_features = find_missing_features(
                X_train,
            )
            self.__union__("_missing_features", _missing_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Missing",
                    "Col_Removed": len(_missing_features),
                    "Col_Kept": len(X_train.columns) - len(_missing_features),
                    "Params": {"max_pct_missing": self.max_pct_missing},
                }
            )
            X_train = remove_features(X_train, _missing_features)

        if filter_highly_concentrated:
            _highly_concentrated_features = find_high_topcat_features(X_train, max_pct_mfv=self.max_pct_mfv)
            self.__union__("_highly_concentrated_features", _highly_concentrated_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Highly Concentrated",
                    "Col_Removed": len(_highly_concentrated_features),
                    "Col_Kept": len(X_train.columns) - len(_highly_concentrated_features),
                    "Params": {"max_pct_mfv": self.max_pct_mfv},
                }
            )
            X_train = remove_features(X_train, _highly_concentrated_features)

        if filter_low_values:
            _low_values_features = find_low_nvalues_features(X_train, min_unique_val=self.min_unique_val)
            self.__union__("_low_values_features", _low_values_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Low Values",
                    "Col_Removed": len(_low_values_features),
                    "Col_Kept": len(X_train.columns) - len(_low_values_features),
                    "Params": {"min_unique_val": self.min_unique_val},
                }
            )
            X_train = remove_features(X_train, _low_values_features)

        X = X[X_train.columns]

        if filter_unstable:
            if self.sample_col is None:
                filter_unstable = False
                warnings.warn("filter unstable not performed since no sample columns defined")
            elif self._n_sample <= 1:
                filter_unstable = False
                warnings.warn("filter unstable not performed since sample columns defined is constant")
            else:
                sample_comb = list(combinations(self._sample_list, 2))
                unstable_dict = {}
                for comb in sample_comb:
                    if (self.sample_train_value in comb) | (self.sample_train_value is None):
                        base = X.loc[sample_series == comb[0]]
                        compare = X.loc[sample_series == comb[1]]
                        unstable_dict[comb] = find_unstable_psi_features(
                            # evetually add a parameter to specify wich combination we are currenty considering
                            base,
                            compare,
                            max_psi=self.max_psi,
                            psi_bin_min_pct=self.psi_bin_min_pct,
                            psi_nbins=self.psi_nbins,
                        )

                _unstable_features = list(reduce(lambda x, y: set(x) | set(y), unstable_dict.values()))
                self.__union__("_unstable_features", _unstable_features)
                self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                    {
                        "Step_Description": "Unstable",
                        "Col_Removed": len(_unstable_features),
                        "Col_Kept": len(X_train.columns) - len(_unstable_features),
                        "Params": {
                            "max_psi": self.max_psi,
                            "psi_bin_min_pct": self.psi_bin_min_pct,
                            "psi_nbins": self.psi_nbins,
                        },
                    }
                )
                X = remove_features(X, _unstable_features)

        if filter_unexplanatory:
            if self.target_col is None:
                filter_unexplanatory = False
                warnings.warn("filter unexplanatory not performed since no target columns defined")
            elif (self.sample_col is None) | (self._n_sample <= 1):
                warnings.warn("filter unexplanatory considering the whole dataset belonging to the same split")
                _unexplanatory_features, _perf_db = find_not_explanatory(
                    X,
                    None,
                    convert_Int_series(y),
                    None,
                    threshold=self.explanatory_threshold,
                    algo_type=self.algo_type,
                    dim_cat_threshold=self.dim_cat_threshold,
                )
                self._perf_db = _perf_db
                self.__union__("_unexplanatory_features", _unexplanatory_features)
                self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                    {
                        "Step_Description": "Unexplanatory",
                        "Col_Removed": len(_unexplanatory_features),
                        "Col_Kept": len(X.columns) - len(_unexplanatory_features),
                        "Params": {
                            "threshold": self.explanatory_threshold,
                            "algo_type": self.algo_type,
                            "dim_cat_threshold": self.dim_cat_threshold,
                        },
                    }
                )
                X = remove_features(X, _unexplanatory_features)
            else:
                sample_comb = list(combinations(self._sample_list, 2))
                unexpl_dict = {}
                perf_dict = {}
                for comb in sample_comb:
                    if (self.sample_train_value in comb) | (self.sample_train_value is None):
                        baseX = X.loc[sample_series == comb[0]]
                        compareX = X.loc[sample_series == comb[1]]
                        basey = y.loc[sample_series == comb[0]]
                        comparey = y.loc[sample_series == comb[1]]
                        unexpl_dict[comb], _perf_ = find_not_explanatory(
                            baseX,
                            compareX,
                            convert_Int_series(basey),
                            convert_Int_series(comparey),
                            threshold=self.explanatory_threshold,
                            algo_type=self.algo_type,
                            dim_cat_threshold=self.dim_cat_threshold,
                        )
                        perf_dict[comb] = _perf_[["name", "perf"]].copy()

                _unexplanatory_features = list(reduce(lambda x, y: set(x) | set(y), unexpl_dict.values()))
                perf_db = reduce(
                    lambda x, y: x.merge(y, left_index=True, right_index=True, how="outer"), perf_dict.values()
                )
                perf_db.set_index("name", inplace=True)
                perf_db["perf"] = perf_db.min(axis=1)
                _perf_db = perf_db[["perf"]].reset_index()
                self._perf_db = _perf_db
                self.__union__("_unexplanatory_features", _unexplanatory_features)
                self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                    {
                        "Step_Description": "Unexplanatory",
                        "Col_Removed": len(_unexplanatory_features),
                        "Col_Kept": len(X.columns) - len(_unexplanatory_features),
                        "Params": {
                            "threshold": self.explanatory_threshold,
                            "algo_type": self.algo_type,
                            "dim_cat_threshold": self.dim_cat_threshold,
                        },
                    }
                )
                X = remove_features(X, _unexplanatory_features)

        X_train = X_train[X.columns]

        if (filter_correlated) & (X_train.shape[1] > 1):
            _correlated_features, selection_history, self._avg_corr = find_correlated_features(
                X_train,
                correlation_threshold=self.correlation_threshold,
                selection_rule=self.selection_rule,
                random_state=self.random_state,
                feat_univ_perf=self._perf_db,
                return_selection_history=self.return_selection_history,
                verbose=self.verbose,
                return_avg_corr=True,
            )
            if self.return_selection_history:
                self._selection_history = pd.concat([self._selection_history, selection_history])
            self.__union__("_correlated_features", _correlated_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Correlated",
                    "Col_Removed": len(_correlated_features),
                    "Col_Kept": len(X_train.columns) - len(_correlated_features),
                    "Params": {
                        "correlation_threshold": self.correlation_threshold,
                        "selection_rule": self.selection_rule,
                        "random_state": self.random_state,
                    },
                }
            )
            X_train = remove_features(X_train, _correlated_features)

        if (filter_collinear) & (len(get_numerical_features(X_train)) > 1):
            if (not self.collinear_optimize) | (not (filter_correlated or filter_unexplanatory)):
                self.collinear_optimize = False
                optim_Series = None
                optim_value_ascending = True

            elif filter_correlated:
                optim_Series = self._avg_corr
                optim_value_ascending = False
            else:
                optim_Series = self._perf_db.set_index("name")["perf"]
                optim_value_ascending = True

            _collinear_features = find_collinear_feature_optimized(
                X_train,
                vif_threshold=self.vif_threshold,
                verbose=self.verbose,
                optimize=self.collinear_optimize,
                optim_Series=optim_Series,
                optim_value_ascending=optim_value_ascending,
            )
            self.__union__("_collinear_features", _collinear_features)
            self._funnel_df.loc[self._funnel_df.shape[0]] = pd.Series(
                {
                    "Step_Description": "Collinear",
                    "Col_Removed": len(_collinear_features),
                    "Col_Kept": len(X_train.columns) - len(_collinear_features),
                    "Params": {
                        "vif_threshold": self.vif_threshold,
                        "optimize": self.collinear_optimize,
                        # I did not put optim_value_ascending cause it is decided automatically
                    },
                }
            )
            X_train = remove_features(X_train, _collinear_features)

        self.filter_constant |= filter_constant
        self.filter_missing |= filter_missing
        self.filter_highly_concentrated |= filter_highly_concentrated
        self.filter_low_values |= filter_low_values
        self.filter_unstable |= filter_unstable
        self.filter_unexplanatory |= filter_unexplanatory
        self.filter_correlated |= filter_correlated
        self.filter_collinear |= filter_collinear

        self.__intersection__("_selected_features", list(X_train.columns))
        self.__union__("_filtered_out_features", list(set(self.feat_to_check) - set(X_train.columns)))
        return

    def find_constant_features(self, **kwargs):
        """Perform the filtering of constant features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=True,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_missing_features(self, **kwargs):
        """Perform the filtering of missing features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=True,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_high_topcat_fetures(self, **kwargs):
        """Perform the filtering of high_topcat features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=True,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_low_nvalues_features(self, **kwargs):
        """Perform the filtering of low_nvalues features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=True,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=False,
        )
        return

    def find_unstable_psi_features(self, **kwargs):
        """Perform the filtering of unstable features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=True,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_not_explanatory(self, **kwargs):
        """Perform the filtering of unexplanatory features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=True,
            filter_correlated=False,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_correlated_features(self, **kwargs):
        """Perform the filtering of correlated features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=True,
            filter_collinear=False,
            **kwargs,
        )
        return

    def find_collinear_feature_optimized(self, **kwargs):
        """Perform the filtering of collinear features.

        It simply call run() method with the correspondent argument as True.
        """
        self.run(
            filter_constant=False,
            filter_missing=False,
            filter_highly_concentrated=False,
            filter_low_values=False,
            filter_unstable=False,
            filter_unexplanatory=False,
            filter_correlated=False,
            filter_collinear=True,
            **kwargs,
        )
        return

    def get_X_original(self):
        """Return the dataset with just the features to check."""
        return self.db[self.feat_to_check]

    def get_X_reduced(self):
        """Return the reduced dataset without the sample_col, target_col and the filtered features."""
        return self.db[self._selected_features]

    def get_db_filtered(self):
        """Return the reduced dataset without the filtered features."""
        return self.db.drop(columns=self._filtered_out_features)

    def make_funnel(self):
        """Return the funnel dataframe."""
        return self._funnel_df

    def make_report(self):
        """Return the feature selection report."""
        attr_list = [
            "_constant_features",
            "_missing_features",
            "_highly_concentrated_features",
            "_low_values_features",
            "_unstable_features",
            "_unexplanatory_features",
            "_correlated_features",
            "_collinear_features",
        ]
        report_list = []

        for attr in attr_list:
            report_list.append(
                pd.DataFrame({"feat_name": self.__dict__[attr], "result": "drop", "drop_reason": attr[1:-9]})
            )
        report_list.append(pd.DataFrame({"feat_name": self._selected_features, "result": "keep"}))

        return pd.concat(report_list).reset_index(drop=True)
