from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def _supported_sklearn_artifacts(**options):
    """ """
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


def _get_pipeline(representation: str, model: str, **options) -> Pipeline:
    """ """

    representation_dict, model_dict = _supported_sklearn_artifacts(**options)

    representation_artifact = representation_dict.get(representation)
    model_artifact = model_dict.get(model)

    if not representation_artifact:
        raise ValueError(
            f"{representation} is not supported. Please select `representation='tfidf'` instead "
        )

    if not model_artifact:
        raise ValueError(
            f"{model_artifact} is not supported. Please select `model='logistic_regression'` instead "
        )

    return Pipeline(
        [(representation, representation_artifact), (model, model_artifact)]
    )
