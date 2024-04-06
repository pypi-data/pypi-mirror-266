import logging
import pandas as pd
import string
import random

from typing import Tuple, List
from pandas._typing import RandomState


class Logger:
    """ """

    def __init__(self, name, level=logging.ERROR):
        """ """
        self.logger = logging.getLogger(name)
        self.set_level(level)

        self._setup_stream_handler()
        self.logger.propagate = False

    def _setup_stream_handler(self):
        """ """
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def set_level(self, level):
        """ """
        self.logger.setLevel(level)

    def info(self, message):
        """ """
        self.logger.info(f"{message}")

    def warning(self, message):
        """ """
        self.logger.warning(f"{message}")


def _check_num_unique_labels(data, y_col_name):
    """ """
    count = len(pd.unique(data[y_col_name]))
    if count <= 1:
        raise ValueError(f"Number of distinct labels should be > 1 " f"Found {count}")


def _check_columns(data, X_col_name, y_col_name):
    """ """
    actual_columns = data.columns.tolist()

    if not X_col_name:
        raise ValueError("'X_col_name' cannot be None. Please pass a valid column name")

    if not y_col_name:
        raise ValueError("'y_col_name' cannot be None ")

    expected_columns = [X_col_name, y_col_name]

    if set(expected_columns) > set(actual_columns):
        raise ValueError(
            f"Data does not contain the expected columns. "
            f"Expected(X_col_name, y_col_name): {expected_columns}, "
            f"Actual: {actual_columns}"
        )


def _check_null_values(data, X_col_name, y_col_name):
    """ """
    if any(data[col].isnull().any() for col in [X_col_name, y_col_name]):
        raise ValueError(
            "Null values found in the data. \
                                 Automatically imputing missing values is not supported yet."
        )


def _is_valid(data, X_col_name, y_col_name):
    """ """
    _check_columns(data, X_col_name, y_col_name)
    _check_num_unique_labels(data, y_col_name)
    _check_null_values(data, X_col_name, y_col_name)


def _fetch_supported_implementations():
    """"""
    return {
        "curate_representation": ["tfidf"],
        "curate_model": ["logistic_regression"],
        "calibration_method": [None, "calibrate_using_baseline"],
    }


def _check_supported(
    curate_representation: str,
    curate_model: str,
    calibration_method: str | ModuleNotFoundError,
):
    supported = _fetch_supported_implementations()
    msg = ""
    if curate_representation not in supported["curate_representation"]:
        msg += f"curate_representation '{curate_representation}' is not supported. "
        msg += (
            f"Currently, {', '.join(supported['curate_representation'])} is supported\n"
        )

    if curate_model not in supported["curate_model"]:
        msg += f"curate_model '{curate_model}' is not supported. "
        msg += f"Currently, {', '.join(supported['curate_model'])} is supported\n"

    if calibration_method not in supported["calibration_method"]:
        msg += f"calibration_method '{calibration_method}' is not supported. "
        msg += f"Currently, {', '.join(map(str, supported['calibration_method']))} are supported\n"

    if len(msg) > 0:
        raise ValueError(msg)


class _DataProcessor:
    def __init__(
        self,
        df: pd.DataFrame,
        random_state: RandomState | None = None,
        y_col_name: str = "label",
        y_col_name_int: str = "label_int",
    ):
        self.df = df
        self.random_state = random_state
        self.y_col_name = y_col_name
        self.y_col_name_int = y_col_name_int
        
        self.newly_added_cols = set([])
        self.row_id_col = None

    def _generate_random_suffix(self, length=3):
        """
        Generates and returns a unique string with letters and/or digits.

        Parameters:
            length (int): Length of the string (default is 3)

        Returns:
            str: Unique short string
        """
        # Define the characters to use in the string
        characters = string.ascii_letters + string.digits

        # Generate a random string of the specified length
        random_string = "".join(random.choices(characters, k=length))

        return random_string

    def _add_row_id(self) -> Tuple[pd.DataFrame, str]:
        """_summary_

        Returns:
            row_id_col (str)
        """
        # Generate a unique column name
        row_id_col = "row_id"

        while row_id_col in self.df.columns:
            row_id_col += f"_{self._generate_random_suffix()}"

        # Add row numbers as a new column
        self.df[row_id_col] = range(1, len(self.df) + 1)

        # Mark this column as a newly added column
        self.newly_added_cols.add(row_id_col)

        return row_id_col

    def _shuffle_data(self) -> pd.DataFrame:
        """_summary_

        Returns:
            pd.DataFrame: _description_
        """
        # Shuffle the dataframe
        self.df = self.df.sample(frac=1.0, 
                                 random_state=self.random_state)\
                         .reset_index(drop=True)

        return

    def _convert_labels_to_int(self):
        """
        Map string labels to integers for downstream processing and return the updated DataFrame
        along with the mapping dictionary.

        Returns:
            pandas.DataFrame: DataFrame with a new integer column.
            dict: Mapping dictionary from string values to integers.
        """

        if not self.df[self.y_col_name].dtype == "object":
            self.df[self.y_col_name_int] = self.df[self.y_col_name]
            return

        # Create a mapping dictionary from string values to integers
        unique_labels = self.df[self.y_col_name].unique()
        label_mapping = {text: i for i, text in enumerate(unique_labels)}

        # Map string values to integers and create a new column
        self.df[self.y_col_name_int] = self.df[self.y_col_name].map(label_mapping)

        self.newly_added_cols.add(self.y_col_name_int)

        return

    def _preprocess(self) -> Tuple[pd.DataFrame, str]:
        """
        Adds the following columns to the DataFrame -
        1) Adds an additional column 'label_int' with integer values for all labels
        2) Adds row numbers if random_state is not 'None'

        Parameters:
            label_column (str): column containing labels with string/integer values
            random_state (RandomState | None):
        Returns:
            pd.DataFrame: Input Dataframe with added columns
            str: Name of the newly added column
        """

        self._convert_labels_to_int()

        if not self.random_state:
            return self.df, None, self.y_col_name_int

        row_id_col = self._add_row_id()
        self.row_id_col = row_id_col
        self._shuffle_data()

        return self.df, row_id_col, self.y_col_name_int

    def _postprocess(self, display_cols: List[str]) -> pd.DataFrame:
        """Removes redundant columns and returns dataframe
        with selected columns to display

        Args:
            df (pd.DataFrame): _description_
            display_cols (List[str]): _description_

        Returns:
            pd.DataFrame: _description_
        """
        
        res = self.df
        row_id_col = self.row_id_col

        if not row_id_col:
            return res[display_cols]
        
        return res.sort_values(by=[row_id_col])\
                    .reset_index(drop=True)[display_cols]
