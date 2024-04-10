from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from typing import Generator, Tuple
import pandas as pd


def _supported_sklearn_artifacts(**options) -> Tuple[dict, dict]:
    """Returns collection of supported artifacts for curation representation and model

    Returns:
        Tuple[dict, dict]: two dictionaries - one for curation representation and one for curation model
    """
    representation_dict = {
        "tfidf": TfidfVectorizer(
            analyzer=options.get("analyzer", "word"),
            ngram_range=options.get("ngram_range", (1, 1)),
            max_features=min(
                options["num_samples"] // 10, options.get("max_features", 1000)
            ),
        )
    }

    model_dict = {"logistic_regression": LogisticRegression()}

    return representation_dict, model_dict


def _get_pipeline(curate_representation: str, curate_model: str, **options) -> Pipeline:
    """Returns the pipeline for a given curation representation and model choice

    Args:
        curate_representation (str): Feature representation method to be used during curation.
        curate_model (str): Machine learning model that is trained with
                     `representation` features during curation.

    Raises:
        ValueError: If a given `curate_representation` or `curate_model` is not supported

    Returns:
        Pipeline: the constructed sklearn pipeline
    """

    representation_dict, model_dict = _supported_sklearn_artifacts(**options)

    representation_artifact = representation_dict.get(curate_representation)
    model_artifact = model_dict.get(curate_model)

    if not representation_artifact:
        raise ValueError(
            f"{curate_representation} is not supported. Please select `representation='tfidf'` instead "
        )

    if not model_artifact:
        raise ValueError(
            f"{model_artifact} is not supported. Please select `model='logistic_regression'` instead "
        )

    return Pipeline(
        [
            (curate_representation, representation_artifact),
            (curate_model, model_artifact),
        ]
    )


def _data_splitter(
    df: pd.DataFrame,
    X_col_name: str,
    y_col_name_int: str,
    strategy: str = "stratified_kfold",
    n_splits: int = 5,
) -> Generator:
    """Splits the data into train and validation to be consumed in CrossValCurate

    Args:
        df (pd.DataFrame): Input data
        X_col_name (str): Column to be used to extract input features
        y_col_name_int (str): Label column in data
        strategy (str, optional): Strategy to use while splitting the data. Defaults to 'stratified_kfold'.
        n_splits (int, optional): The number of splits. Defaults to 5.

    Returns:
        StratifiedKFold: Currently, a StratifiedKFold object.
    """

    if strategy == "stratified_kfold":
        cv = StratifiedKFold(n_splits=n_splits, shuffle=False, random_state=None)
        return cv.split(df[X_col_name], df[y_col_name_int])

    raise ValueError(
        f"Data splitting strategy {strategy} not supported. Please use `strategy='stratified_kfold'`"
    )
