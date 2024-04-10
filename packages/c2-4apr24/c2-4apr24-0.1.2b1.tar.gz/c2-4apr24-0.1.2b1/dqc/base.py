from abc import ABC, abstractmethod
from dqc.utils import _check_supported
from typing import Union
from pandas._typing import RandomState


class BaseCurate(ABC):
    """Base class for data curation to compute label correctness scores
      and identify reliable labelled samples
    Args:
        curate_representation (str, optional): Feature representation method to be used during curation.
        Defaults to 'tfidf' (`sklearn.feature_extraction.text.TfidfVectorizer`).
        curate_model (str, optional): Machine learning model that is trained with
                     `curate_representation` features during curation.
        Defaults to 'logistic_regression' (sklearn.linear_model.LogisticRegression).
        calibration_method (Union[str, None], optional): Approach to be used for calibration
                    of `curate_model` predictions. Defaults to None.
        correctness_threshold (float, optional): Minimum prediction probability using
          `curate_model` to consider the corresponding sample as 'correctly labelled'.
          Defaults to 0.8.
        random_state (RandomState, optional): Random seed for
                                reproducibility. Defaults to None.
    """

    def __init__(
        self,
        curate_representation: str = "tfidf",
        curate_model: str = "logistic_regression",
        calibration_method: Union[str, None] = None,
        correctness_threshold: float = 0.8,
        random_state: RandomState = 73,
        **options,
    ):
        self.curate_representation = curate_representation.lower()
        self.curate_model = curate_model.lower()
        self.calibration_method = calibration_method

        _check_supported(curate_representation, curate_model, calibration_method)

        self.correctness_threshold = correctness_threshold
        self.random_state = random_state

    @abstractmethod
    def fit_transform(self): ...
