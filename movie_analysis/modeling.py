from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_FEATURE_COLUMNS = [
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


def _resolve_feature_sets(target_column: str) -> tuple[list[str], list[str], list[str]]:
    feature_columns = [column for column in BASE_FEATURE_COLUMNS if column != target_column]
    numeric_features = [column for column in NUMERIC_FEATURES if column != target_column]
    categorical_features = [column for column in CATEGORICAL_FEATURES if column != target_column]
    return feature_columns, numeric_features, categorical_features


def _build_preprocessor(target_column: str) -> ColumnTransformer:
    _, numeric_features, categorical_features = _resolve_feature_sets(target_column)
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
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
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

    feature_columns, _, _ = _resolve_feature_sets(target_column)
    X = modeling_frame[feature_columns]
    y = modeling_frame[target_column].astype(float)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    cv_splits = min(5, len(modeling_frame) // 8)
    cv = KFold(n_splits=max(3, cv_splits), shuffle=True, random_state=42)

    evaluations: list[dict[str, Any]] = []
    best_name = ""
    best_score = -np.inf
    best_test_bundle: dict[str, Any] | None = None
    evaluation_by_name: dict[str, dict[str, Any]] = {}

    for name, estimator in _build_model_catalog().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", _build_preprocessor(target_column)),
                ("model", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        cv_r2_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="r2")
        cv_rmse_scores = np.sqrt(-cross_val_score(pipeline, X, y, cv=cv, scoring="neg_mean_squared_error"))

        mae = mean_absolute_error(y_test, predictions)
        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        r2 = r2_score(y_test, predictions)
        safe_actual = np.where(np.abs(y_test.to_numpy()) < 1e-9, np.nan, y_test.to_numpy())
        ape = np.abs((y_test.to_numpy() - predictions) / safe_actual) * 100
        mape = float(np.nanmean(ape)) if not np.isnan(ape).all() else np.nan
        approx_accuracy = float(max(0.0, 100.0 - mape)) if not np.isnan(mape) else np.nan
        evaluations.append(
            {
                "Model": name,
                "MAE": mae,
                "RMSE": rmse,
                "R2": r2,
                "CV_R2": float(np.mean(cv_r2_scores)),
                "CV_RMSE": float(np.mean(cv_rmse_scores)),
                "MAPE": mape,
                "Approx_Accuracy": approx_accuracy,
            }
        )
        evaluation_by_name[name] = evaluations[-1]

        ranking_score = float(np.mean(cv_r2_scores))
        if ranking_score > best_score:
            best_score = ranking_score
            best_name = name
            best_test_bundle = {
                "predictions": predictions,
                "actual": y_test.to_numpy(),
                "model": pipeline,
            }

    leaderboard = pd.DataFrame(evaluations).sort_values(by="R2", ascending=False).reset_index(drop=True)
    best_model = Pipeline(
        steps=[
            ("preprocessor", _build_preprocessor(target_column)),
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
        "best_model_metrics": evaluation_by_name[best_name],
        "best_model": best_model,
        "feature_importance": feature_importance,
        "prediction_frame": prediction_frame,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "target_column": target_column,
        "feature_columns": feature_columns,
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
    feature_columns = model_bundle["feature_columns"]
    input_frame = pd.DataFrame([{column: payload[column] for column in feature_columns}], columns=feature_columns)
    prediction = float(model_bundle["best_model"].predict(input_frame)[0])

    if target_column == "rating":
        return float(np.clip(prediction, 0.0, 10.0))
    return max(prediction, 0.0)
