from cefeste import FeatureAnalysis
from cefeste.utils import get_categorical_features, convert_Int_series, convert_Int_dataframe
from cefeste.elimination.shap_rfe import Shap_RFE_full
import warnings

from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold


class FeatureElimination(FeatureAnalysis):
    """Child class of FeatureAnalysis for Feature Elimination."""

    def __init__(
        self,
        # DB / Feature Parameters / Model
        db,
        target_col,
        model,
        grid,
        feat_to_check=None,
        sample_col=None,
        sample_train_value=None,
        algo_type="auto",
        # Hyperparameters Tuning / Cross Validation Fold
        cv_funct=RandomizedSearchCV,
        cv_scoring="auto",
        n_iter=20,
        manage_groups=False,
        groups=None,
        cv_type=StratifiedKFold(5, random_state=42, shuffle=True),
        use_ohe=False,
        # Reporting
        step_size=0.1,
        min_n_feat_step=5,
        final_n_feature=1,
        verbose=True,
        write_final=False,
        write_substep=False,
        dim_cat_threshold=10,
    ):
        """Feature Elimination Class.

        Args:
            db (pd.DataFrame): DataFrame to analyze.
            target_col (str): Name of the target column.
            model : classifier or regressor in sklearn API class.
            grid (dict): hyperparameters grid.
            feat_to_check (list, optional): Feature to analyze. If None all are used. Defaults to None.
            sample_col (str, optional): Name of the columns that indicates the samples (train, test). Defaults to None.
            sample_train_value (str, optional): Value of the sample column that indicates the train set. Defaults to None.
            algo_type (str, optional): "auto", "classification", "multiclass", "regression", describes the problem type.
                "classification" has to be used only for binary classification. Defaults to "auto".
            cv_funct: function or class for the Cross Validation. Defaults to RandomizedSearchCV
            cv_scoring: scoring argument of the cv_functs. Defaults to "auto" selects "roc_auc" fo classification, "r2" for regression
                and "balanced accuracy" for multiclass.
            n_iter (int, optional): number of iteration, i.e. set of hyperparams tested in Cross Validation. Defaults to 20.
            manage_groups (bool, optional): determines if there is a feature whose groups have to be kept joined in CV. Defaults to False.
            groups (pd.Series, optional): feature whose groups have to be kept joined in CV. Defaults to None.
            cv_type : function or class for defining the CV sets. Defaults to StratifiedKFold(5, random_state=42, shuffle=True).
            use_ohe (bool, optional): determines whether to use One Hot Encoding on categorical features or not. Defaults to False.
            step_size (int or float, optional): determines how many features to remove at each step.
                Fixed int or percentage of total features. Defaults to 0.1.
            min_n_feat_step (int, optional): min number of feature to remove at each step. Defaults to 5.
            final_n_feature (int, optional): number of features of the last model. Defaults to 1.
            verbose (bool, optional): If True print a log of information. Defaults to True.
            write_final (bool, optional): If True it saves in the current directory the final report that can be used for quick start. Defaults to False.
            write_substep (bool, optional): If True it saves in the current directory the report after SHAP_RFE that can be used for quick start. Defaults to False.
            dim_cat_threshold (int, optional): cardinality threshold for categorical variables to apply or not 'simplified' OHE.
                Defaults to 10.

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
            self._n_sample = None
        # Sample Train value
        if (sample_train_value is not None) & (sample_train_value not in self._sample_list):
            raise ValueError(
                f"The value {sample_train_value} set for parameter sample_train_value is not in {sample_col}."
            )
        else:
            self.sample_train_value = sample_train_value

        # Parameters
        self.model = model
        self.grid = grid
        self.cv_funct = cv_funct
        self.cv_scoring = cv_scoring
        self.n_iter = n_iter
        self.manage_groups = manage_groups
        self.groups = groups
        self.cv_type = cv_type
        self.use_ohe = use_ohe
        self.step_size = step_size
        self.min_n_feat_step = min_n_feat_step
        self.final_n_feature = final_n_feature
        self.verbose = verbose
        self.write_final = write_final
        self.write_substep = write_substep
        self.dim_cat_threshold = dim_cat_threshold
        self.report = None
        self.final_feat = []
        self.selection_rule = None
        self.number_feat_rep = None
        self._filtered_out_features = []

    def make_report(self, **kwargs):
        """Perform the SHAP RFE report.

        Returns:
            pd.DataFrame: shap report
        """
        self.set_params(**kwargs)
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
            raise ValueError("shap rfe not performed since no target column defined")
        X = X[self.feat_to_check]

        if self.sample_train_value is not None:
            X_train = X.loc[sample_series == self.sample_train_value]
            y_train = y.loc[sample_series == self.sample_train_value]
        else:
            X_train = X
            y_train = y

        # Groups check
        if self.manage_groups:
            if self.groups is None:
                warnings.warn("no group defined")
                self.manage_groups = False
            elif not self.groups.index.equals(self.db.index):
                raise ValueError("Groups Series index do not match with DataFrame index in input!")
            else:
                self.groups = self.groups.reset_index(drop=True).iloc[X_train.index]
        else:
            self.groups = None

        # Categorical Features for One Hot Encoding
        if self.use_ohe:
            self.categorical_features_list_ohe = get_categorical_features(X_train)
        else:
            self.categorical_features_list_ohe = []

        shap_report = Shap_RFE_full(
            convert_Int_dataframe(X_train),
            convert_Int_series(y_train),
            model=self.model,
            grid=self.grid,
            cv_funct=self.cv_funct,
            cv_scoring=self.cv_scoring,
            n_iter=self.n_iter,
            manage_groups=self.manage_groups,
            groups=self.groups,
            cv_type=self.cv_type,
            algo_type=self.algo_type,
            step_size=self.step_size,
            min_n_feat_step=self.min_n_feat_step,
            final_n_feature=self.final_n_feature,
            verbose=self.verbose,
            write_final=self.write_final,
            write_substep=self.write_substep,
            use_ohe=self.use_ohe,
            categorical_features_list_ohe=self.categorical_features_list_ohe,
            dim_cat_threshold=self.dim_cat_threshold,
        )

        self.report = shap_report

        return self.report

    def plot_report(self):
        """Plot the report train and validation score."""
        if self.report is not None:
            self.report.plot(
                x="n_feat", y=["train_score", "valid_score"], xlim=(max(self.report.n_feat), min(self.report.n_feat))
            )
        else:
            raise ValueError("Missing report, run .make_report() first")

    def extract_features(self, selection_rule="decrease_perf", number_feat_rep=None, gap=0.1, alpha=0.5):
        """Extract survived features after SHAP RFE.

        Args:
            selection_rule (str, optional): "decrease_perf", "best_valid", "num_feat", "robust_tradeoff" describes the rule for which the features after shap are chosen. Defaults to 'decrease_perf'.
            number_feat_rep (int, optional): valid only for the selection_rule "num_feat", determines the number of features to be extracted according to the report. Defaults to None.
            gap(float, optional): valid only for the selection_rule "decrease_perf", identifies the maximum gap over which the decrease in performance is not acceptable.
            alpha(float, optional): valid only fot the selection_rule "robust_tradeoff", determines which term is preferred betweeen robustness and average performances in the formula
            α * Average_Perf - (1-α) * Gap_Robust
        Returns:
            list: list of features extracted after SHAP RFE according to the selection_rule.
        """
        self.selection_rule = selection_rule
        self.number_feat_rep = number_feat_rep
        self.gap = gap
        self.alpha = alpha
        # Check the target var and set the algo type
        if selection_rule not in ["decrease_perf", "best_valid", "num_feat", "robust_tradeoff"]:
            raise ValueError(
                f"{selection_rule} is not a valid selection_rule. It should be one of the following:\n ['decrease_perf', 'best_valid', 'num_feat', 'robust_tradeoff']"
            )

        if self.report is not None:
            if selection_rule == "decrease_perf":
                # Define n_feat: the first time the validation score decreases of more than 10%
                cutoff = (
                    self.report[["n_feat", "valid_score"]]
                    .sort_values("n_feat", ascending=False)
                    .assign(max_until=lambda x: x.valid_score.expanding().max())
                    .assign(valid_next=lambda x: x.valid_score.shift(periods=-1))
                    .assign(
                        gap=lambda x: x.apply(
                            lambda y: (y.max_until / y.valid_next) - 1
                            if y.valid_next > 0
                            else 1 - (y.max_until / y.valid_next),
                            axis=1,
                        )
                    )
                    .loc[lambda x: x.gap > gap]
                )
                if cutoff.shape[0] < 1:
                    cutoff = self.report.loc[self.report.n_feat.idxmin(), "n_feat"]
                else:
                    cutoff = cutoff.loc[lambda x: x.n_feat.idxmax(), "n_feat"]

                self.final_feat = list(self.report.loc[self.report["n_feat"] == cutoff, "feat_used"])[0]

            elif selection_rule == "best_valid":
                # Define n_feat: best validation score iteration
                n_min_feat = self.report.loc[
                    self.report["valid_score"] == self.report["valid_score"].max(), "n_feat"
                ].min()
                self.final_feat = list(self.report.loc[self.report["n_feat"] == n_min_feat, "feat_used"])[0]

            elif selection_rule == "robust_tradeoff":
                # Define n_feat: best score of the formula α * Average_Perf - (1-α) * Gap_Robust
                adding_report = (
                    self.report[["n_feat", "train_score", "valid_score"]]
                    .assign(avg_scoring=lambda x: (x.train_score + x.valid_score) / 2)
                    .assign(gap_ratio=lambda x: abs(x.train_score - x.valid_score))
                    .assign(avg_scoring=lambda x: (x.avg_scoring - x.avg_scoring.mean()) / x.avg_scoring.std())
                    .assign(gap_ratio=lambda x: (x.gap_ratio - x.gap_ratio.mean()) / x.gap_ratio.std())
                    .assign(tradeoff_robust_avg_scoring=lambda x: (alpha * x.avg_scoring - (1 - alpha) * x.gap_ratio))
                )
                n_min_feat = adding_report.loc[
                    lambda x: x.tradeoff_robust_avg_scoring == x.tradeoff_robust_avg_scoring.max(),
                    "n_feat",
                ].min()
                self.final_feat = list(self.report.loc[self.report["n_feat"] == n_min_feat, "feat_used"])[0]

            else:
                # Define n_feat: the user choose the features to use according to number of features to be used
                if number_feat_rep is not None:
                    try:
                        self.final_feat = list(self.report.loc[self.report["n_feat"] == number_feat_rep, "feat_used"])[
                            0
                        ]
                    except Exception:
                        raise ValueError(f"{number_feat_rep} number of features chosen uncorrect, look the report")
                else:
                    self.final_feat = list(
                        self.report.loc[self.report["n_feat"] == self.report["n_feat"].max(), "feat_used"]
                    )[0]
        else:
            raise ValueError("Missing report, run .make_report() first")

        self._filtered_out_features = list(set(self.feat_to_check) - set(self.final_feat))
        return self.final_feat

    def get_X_original(self):
        """Return the dataset with just the features to check."""
        return self.db[self.feat_to_check]

    def get_X_reduced(self):
        """Return the reduced dataset without the sample_col, target_col and the filtered features."""
        return self.db[self.final_feat]

    def get_db_filtered(self):
        """Return the reduced dataset without the filtered features."""
        return self.db.drop(columns=self._filtered_out_features)
