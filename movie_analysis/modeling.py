from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURE_COLUMNS = [
    "budget",
    "runtime",
    "release_year",
    "vote_count",
    "metascore",
    "primary_genre",
    "studio",
    "language",
]
NUMERIC_FEATURES = ["budget", "runtime", "release_year", "vote_count", "metascore"]
CATEGORICAL_FEATURES = ["primary_genre", "studio", "language"]


def _build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )


def _build_model_catalog() -> dict[str, Any]:
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=320,
            max_depth=12,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }


def train_regression_models(frame: pd.DataFrame, target_column: str) -> dict[str, Any]:
    if target_column not in frame.columns:
        raise ValueError(f"Target column '{target_column}' not found.")

    modeling_frame = frame.dropna(subset=[target_column]).copy()
    if len(modeling_frame) < 30:
        raise ValueError("Not enough records to train a prediction model.")

    X = modeling_frame[FEATURE_COLUMNS]
    y = modeling_frame[target_column].astype(float)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    evaluations: list[dict[str, Any]] = []
    best_name = ""
    best_score = -np.inf
    best_test_bundle: dict[str, Any] | None = None

    for name, estimator in _build_model_catalog().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", _build_preprocessor()),
                ("model", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        r2 = r2_score(y_test, predictions)
        evaluations.append(
            {
                "Model": name,
                "MAE": mae,
                "RMSE": rmse,
                "R2": r2,
            }
        )

        if r2 > best_score:
            best_score = r2
            best_name = name
            best_test_bundle = {
                "predictions": predictions,
                "actual": y_test.to_numpy(),
                "model": pipeline,
            }

    leaderboard = pd.DataFrame(evaluations).sort_values(by="R2", ascending=False).reset_index(drop=True)
    best_model = Pipeline(
        steps=[
            ("preprocessor", _build_preprocessor()),
            ("model", _build_model_catalog()[best_name]),
        ]
    )
    best_model.fit(X, y)

    feature_importance = _extract_feature_importance(best_model).head(12)
    prediction_frame = pd.DataFrame(
        {
            "actual": best_test_bundle["actual"],
            "predicted": best_test_bundle["predictions"],
        }
    )
    return {
        "leaderboard": leaderboard,
        "best_model_name": best_name,
        "best_model": best_model,
        "feature_importance": feature_importance,
        "prediction_frame": prediction_frame,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "target_column": target_column,
    }


def _extract_feature_importance(best_model: Pipeline) -> pd.DataFrame:
    preprocessor = best_model.named_steps["preprocessor"]
    model = best_model.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()

    if hasattr(model, "feature_importances_"):
        raw_importance = np.asarray(model.feature_importances_)
    elif hasattr(model, "coef_"):
        raw_importance = np.abs(np.asarray(model.coef_))
    else:
        raw_importance = np.zeros(len(feature_names))

    importance = pd.DataFrame({"feature": feature_names, "importance": raw_importance})
    importance["feature"] = importance["feature"].str.replace("num__", "", regex=False)
    importance["feature"] = importance["feature"].str.replace("cat__", "", regex=False)
    importance["feature"] = importance["feature"].str.replace("_", " ", regex=False).str.title()
    return importance.sort_values(by="importance", ascending=False).reset_index(drop=True)


def predict_single(model_bundle: dict[str, Any], payload: dict[str, Any], target_column: str) -> float:
    input_frame = pd.DataFrame([payload], columns=FEATURE_COLUMNS)
    prediction = float(model_bundle["best_model"].predict(input_frame)[0])

    if target_column == "rating":
        return float(np.clip(prediction, 0.0, 10.0))
    return max(prediction, 0.0)
