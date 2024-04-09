from cefeste.utils import get_categorical_features, get_numerical_features
import warnings


class FeatureAnalysis:
    """Feature Analysis base class."""

    def __init__(self, db, feat_to_check=None):
        """Initialize the class.

        Args:
            db (pd.DataFrame): DataFrame to analyze
            feat_to_check (list, optional): Feature to analyze. If None all are used. Defaults to None.
        """
        self.db = db
        if feat_to_check is None:
            feat_to_check = db.columns

        self.feat_to_check = feat_to_check
        self.categorical_features = get_categorical_features(
            db[feat_to_check],
        )
        self.numerical_features = get_numerical_features(
            db[feat_to_check],
        )

    def get_params(self, params=None):
        """Get a parameter of the class.

        Args:
            params (str, optional): name of the parameter for which the value has to be returned.
                If None all are returned. Defaults to None.

        Raises:
            ValueError: In case the parameters required do not exist.

        Returns:
            Value of the parameter
        """
        if params is None:
            return self.__dict__
        elif params in self.__dict__.keys():
            return self.__dict__[params]
        else:
            raise ValueError(f"Parameters {params} is not a parameter of the class")

    def set_params(self, exceptions=None, **kwargs):
        """Set the parameter of the class.

        Raises:
            ValueError: In case an unknown parameter has been set.
        """
        if exceptions is None:
            exceptions = []
        for k, v in kwargs.items():
            if k in self.__dict__.keys():
                if k in exceptions:
                    warnings.warn(f"Parameter {k} cannot be overwritten")
                else:
                    self.__dict__[k] = v
            else:
                raise ValueError(f"Parameter {k} is not a parameter of the class")

    def eda(self):
        """Generate Exploratory Data Analysis.

        Returns:
            dict: Dictionary with describe or value counts.
        """
        analysis = dict()
        for col in self.numerical_features:
            analysis[col] = self.db[col].describe()
        for col in self.categorical_features:
            analysis[col] = self.db[col].value_counts()
        return analysis

    def __union__(self, attr_name, new_list):
        """It perform the union between the list stored in the attribute named 'attr_name' and 'new_list' and assign the result to the attribute.

        Args:
            attr_name (str): name of the attribute we want to update
            new_list (list): list we want to merge
        """
        old_list = getattr(self, attr_name)
        setattr(self, attr_name, list(set(old_list).union(set(new_list))))

    def __intersection__(self, attr_name, new_list):
        """It perform the inersection between the list stored in the attribute named 'attr_name' and 'new_list' and assign the result to the attribute.

        Args:
            attr_name (str): name of the attribute we want to update
            new_list (list): list we want to intersecate
        """
        old_list = getattr(self, attr_name)
        setattr(self, attr_name, list(set(old_list).intersection(set(new_list))))
