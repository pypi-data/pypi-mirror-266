from abc import ABC, abstractmethod
from dqc.utils import _check_supported


class BaseCurate(ABC):
    def __init__(
        self,
        curate_representation: str = "tfidf",
        curate_model: str = "logistic_regression",
        calibration_method: str | None = None,
        correctness_threshold: float = 0.8,
        random_state=None,
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
