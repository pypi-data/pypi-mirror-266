from dqc.base import BaseCurate
from dqc.utils import Logger, _get_pipeline, _is_valid, _DataProcessor

from sklearn.model_selection import KFold
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
import numpy as np
import pandas as pd
from typing import Union, List, Tuple

logger = Logger("C2")

tqdm.pandas()


class CrossValCurate(BaseCurate):
    """ """

    def __init__(self, n_splits: int = 5, **options):
        """_summary_

        Args:
            n_splits (int, optional): _description_. Defaults to 5.
            Initializing CrossValCurate

        Args:
            curate_representation (str, optional): Choice of feature representation.
            Defaults to 'tfidf' (`sklearn.feature_extraction.text.TfidfVectorizer`).
            curate_model (str, optional): Choice of machine learning classifier.
            Defaults to 'logistic_regression' (sklearn.linear_model.LogisticRegression).

            n_splits (int, optional): Number of splits to use when running cross-validation based curation. Defaults to 5.
        """
        super().__init__(**options)
        self.n_splits = n_splits
        self.curate_pipeline = None
        self.scaler = None
        self.y_col_name_int = None
        self.result_col_list = [
            "label_correctness_score",
            "is_label_correct",
            "predicted_label",
            "prediction_probability",
        ]

    def __str__(self):
        return str(self.__dict__)

    def _is_confident(self, row: pd.Series) -> bool:
        """Return a boolean variable indicating whether we are confident
           about the correctness of the label assigned to a given data sample

        Args:
            row (pd.Series): data sample whose label correctness need to be evaluated

        Returns:
            bool: `True` if we are confident that the label assigned is correct
                else `False`
        """
        threshold = self.correctness_threshold
        if (row["predicted_label"] == row[self.y_col_name_int]) and (
            row["label_correctness_score"] > threshold
        ):
            return True
        return False

    def _no_calibration(
        self,
        input_labels: List[Union[int, str]],
        pred_prob_matrix: np.ndarray,
        label_list: List[Union[int, str]],
    ) -> Tuple[List[Union[int, str]], List[float]]:
        """_summary_

        Args:
            input_labels (List[Union[int, str]]): _description_
            pred_prob_matrix (np.ndarray): _description_
            label_list (List[Union[int, str]]): _description_

        Returns:
            Tuple[List[Union[int, str]], List[float]]: _description_
        """
        pred_probs = np.max(pred_prob_matrix, axis=1).tolist()
        preds = [label_list[index] for index in np.argmax(pred_prob_matrix, axis=1)]
        label_correctness_scores = [
            pred_prob_matrix[row_index, label_list.index(label)]
            for row_index, label in enumerate(input_labels)
        ]
        return preds, pred_probs, label_correctness_scores

    def _get_baselines(self, data_with_noisy_labels: pd.DataFrame) -> pd.DataFrame:
        """Computes the baseline prediction probabilities using
          input label distribution

        Args:
            data_with_noisy_labels (pd.DataFrame): Input data with corresponding noisy labels

        Returns:
            pd.DataFrame: Labels and corresponding probabilities
        """
        thresholds_df = (
            data_with_noisy_labels[self.y_col_name_int].value_counts(1)
        ).reset_index()
        thresholds_df.columns = [self.y_col_name_int, "probability"]
        return thresholds_df

    def _calibrate_using_baseline(
        self,
        input_labels: List[Union[int, str]],
        pred_prob_matrix: np.ndarray,
        label_list: List[Union[int, str]],
        baseline_probs: pd.DataFrame,
    ) -> Tuple[List[Union[int, str]], List[float], List[float]]:
        """_summary_

        Args:
            input_labels (List[Union[int, str]]): _description_
            pred_prob_matrix (np.ndarray): _description_
            label_list (List[Union[int, str]]): _description_
            baseline_probs (pd.DataFrame): _description_

        Returns:
            Tuple[List[Union[int, str]], List[float], List[float]]:
            Returns the following
            'calibrated_prediction' : Label predictions post calibration
            'calibrated_probabilities' : Normalized scores corresponding
                                    to 'calibrated_prediction'
            'label_correctness_score' : Normalized scores corresponding
                                     to 'label' (provided as input to
                                    `fit_transform`)
        """

        label_list_df = pd.DataFrame({"label_list": label_list})
        baseline_probs = pd.merge(
            label_list_df,
            baseline_probs,
            left_on="label_list",
            right_on=self.y_col_name_int,
            how="inner",
        ).reset_index(drop=True)

        baseline_probs.drop("label_list", axis=1, inplace=True)

        prob_array = baseline_probs["probability"].values
        pred_prob_matrix = (pred_prob_matrix - prob_array) / prob_array

        if not self.scaler:
            self.scaler = MinMaxScaler()

        pred_prob_matrix = self.scaler.fit_transform(pred_prob_matrix)

        calibrated_predictions = [
            label_list[index] for index in np.argmax(pred_prob_matrix, axis=1)
        ]
        calibrated_probabilities = np.max(pred_prob_matrix, axis=1).tolist()
        label_correctness_scores = [
            pred_prob_matrix[row_index, label_list.index(label)]
            for row_index, label in enumerate(input_labels)
        ]

        return (
            calibrated_predictions,
            calibrated_probabilities,
            label_correctness_scores,
        )

    def fit_transform(
        self,
        data_with_noisy_labels: pd.DataFrame,
        X_col_name: str = "text",
        y_col_name: str = "label",
        **options,
    ) -> pd.DataFrame:
        """Fit CrossValCurate on the given data

        Args:
            data_with_noisy_labels (pd.DataFrame): Input data with corresponding noisy labels

        Returns:
            pd.DataFrame: Input Data samples with
                1) Corresponding predicted_labels using CrossValCurate
                2) Prediction probabilities
                3) An indicator variable `is_confident` capturing label correctness
        """
        _is_valid(data_with_noisy_labels, X_col_name, y_col_name)
        n_splits = self.n_splits
        options["num_samples"] = len(data_with_noisy_labels)

        logger.info("Pre-processing the data..")
        dp = _DataProcessor(
            data_with_noisy_labels,
            random_state=self.random_state,
            y_col_name=y_col_name,
        )

        data_with_noisy_labels, row_id_col, y_col_name_int = dp._preprocess()

        # y_col_name_int needs to be accessed downstream
        self.y_col_name_int = y_col_name_int

        data_columns = [X_col_name, y_col_name_int]

        logger.info(
            "Building the curation pipeline with {n_splits}-fold cross validation.."
        )
        self.curate_pipeline = _get_pipeline(
            self.curate_representation, self.curate_model, **options
        )

        cv = KFold(n_splits=n_splits, shuffle=False, random_state=None)

        # Lists to store predictions
        predictions = []
        prediction_probabilities = []
        label_correctness_scores = []

        if self.calibration_method == "calibrate_using_baseline":
            logger.info("Computing baseline predictions for each label..")
            baseline_probs = self._get_baselines(data_with_noisy_labels[data_columns])

        # Iterate through kfold splits
        for train_index, val_index in tqdm(
            cv.split(data_with_noisy_labels[data_columns])
        ):
            # Split the data
            X_train, X_val = (
                data_with_noisy_labels.loc[train_index, X_col_name].values,
                data_with_noisy_labels.loc[val_index, X_col_name].values,
            )
            y_train, y_val = (
                data_with_noisy_labels.loc[train_index, y_col_name_int].values,
                data_with_noisy_labels.loc[val_index, y_col_name_int].values,
            )

            # Train the model
            self.curate_pipeline.fit(X_train, y_train)
            classes_ = self.curate_pipeline.classes_.tolist()

            # Make predictions on the validation set
            y_pred_probs = self.curate_pipeline.predict_proba(X_val)

            if self.calibration_method == "calibrate_using_baseline":
                y_preds, y_pred_probs, label_cscores = self._calibrate_using_baseline(
                    y_val,
                    y_pred_probs,
                    label_list=classes_,
                    baseline_probs=baseline_probs,
                )
            else:
                y_preds, y_pred_probs, label_cscores = self._no_calibration(
                    y_val, y_pred_probs, label_list=classes_
                )

            predictions.extend(y_preds)
            prediction_probabilities.extend(y_pred_probs)
            label_correctness_scores.extend(label_cscores)

        # Add results as columns
        data_with_noisy_labels["label_correctness_score"] = pd.Series(
            label_correctness_scores
        )
        data_with_noisy_labels["predicted_label"] = pd.Series(predictions)
        data_with_noisy_labels["prediction_probability"] = pd.Series(
            prediction_probabilities
        )

        logger.info("Identifying the correctly labelled samples..")
        data_with_noisy_labels["is_label_correct"] = (
            data_with_noisy_labels.progress_apply(self._is_confident, axis=1)
        )

        return dp._postprocess(display_cols=data_columns + self.result_col_list)
