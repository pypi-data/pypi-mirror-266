import pytest
from dqc import CrossValCurate
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
    data = cvc.fit_transform(data)

    # Check if dataframe is return
    assert type(data) == pd.DataFrame

    # Check column presence
    assert all(
        col in data.columns
        for col in [
            "prediction_probability",
            "predicted_label",
            "label_correctness_score",
            "is_label_correct",
        ]
    )

    # Check data types
    assert all(
        data[col].dtype == dtype
        for col, dtype in [
            ("prediction_probability", float),
            ("label_correctness_score", float),
            ("is_label_correct", bool),
        ]
    )

    # Check non-null values
    assert all(
        data[col].notnull().all()
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
