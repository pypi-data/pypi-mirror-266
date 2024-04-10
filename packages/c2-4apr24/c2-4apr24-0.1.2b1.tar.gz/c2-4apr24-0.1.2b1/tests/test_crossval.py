import pytest
from dqc import CrossValCurate
from dqc.utils import add_asymmetric_noise
import pandas as pd


@pytest.mark.parametrize("curate_representation", ["tfidf", "TfIdf"])
@pytest.mark.parametrize(
    "curate_model",
    ["logistic_regression", "Logistic_Regression"],
)
@pytest.mark.parametrize("calibration_method", [None, "calibrate_using_baseline"])
@pytest.mark.parametrize("random_state", [None, 1])
def test_crossvalcurate_success(
    data, curate_representation, curate_model, calibration_method, random_state
):
    cvc = CrossValCurate(
        calibration_method=calibration_method, random_state=random_state
    )
    data_curated = cvc.fit_transform(data)

    # Check if dataframe is return
    assert type(data_curated) == pd.DataFrame

    # Check column presence
    assert all(
        col in data_curated.columns
        for col in [
            "prediction_probability",
            "predicted_label",
            "label_correctness_score",
            "is_label_correct",
        ]
    )

    # Check data types
    assert all(
        data_curated[col].dtype == dtype
        for col, dtype in [
            ("prediction_probability", float),
            ("label_correctness_score", float),
            ("is_label_correct", bool),
        ]
    )

    # Check non-null values
    assert all(
        data_curated[col].notnull().all()
        for col in [
            "prediction_probability",
            "predicted_label",
            "label_correctness_score",
            "is_label_correct",
        ]
    )


@pytest.mark.parametrize("curate_representation", ["tf_idf", 1, ""])
@pytest.mark.parametrize(
    "curate_model",
    ["logistic regression", 2, ""],
)
@pytest.mark.parametrize("calibration_method", ["random", 3, ""])
@pytest.mark.parametrize("random_state", ["randomstr", ""])
def test_crossvalcurate_failure(
    data, curate_representation, curate_model, calibration_method, random_state
):
    with pytest.raises(ValueError):
        cvc = CrossValCurate(
            calibration_method=calibration_method, random_state=random_state
        )
        data = cvc.fit_transform(data)


def test_crossvalcurate_datafailure(data):
    with pytest.raises(ValueError):
        cvc = CrossValCurate()
        data = data.groupby("label", group_keys=False).sample(
            frac=0.005, random_state=43
        )
        data = cvc.fit_transform(data)


@pytest.mark.parametrize("calibration_method", [None, "calibrate_using_baseline"])
@pytest.mark.parametrize("verbose", [True, False])
def test_verbosity(data, calibration_method, verbose):
    cvc = CrossValCurate(calibration_method=calibration_method, verbose=verbose)
    data = cvc.fit_transform(data)


@pytest.mark.parametrize("noise_prob", [0.1])
@pytest.mark.parametrize("random_state", [None, 1])
def test_add_asymmetric_noise(data, noise_prob, random_state):
    noisy_labels = add_asymmetric_noise(
        data["label"], noise_prob=noise_prob, random_state=random_state
    )

    assert isinstance(noisy_labels, pd.Series)
    assert len(noisy_labels) == len(data["label"])
