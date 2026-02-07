from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


FEATURE_NAMES: tuple[str, ...] = ("distance", "cum_altitude_gain", "is_trail")
TARGET_NAME = "elapsed_seconds"


@dataclass(frozen=True)
class FeatureMatrix:
    X: np.ndarray
    y: np.ndarray
    feature_names: tuple[str, ...]
    feature_means: np.ndarray


def _validate_columns(df: pd.DataFrame) -> None:
    required = ("distance", "cum_altitude_gain", "sub_sport", TARGET_NAME)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _sub_sport_to_is_trail(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().eq("trail").astype(float)


def build_training_matrix(df: pd.DataFrame) -> FeatureMatrix:
    _validate_columns(df)

    frame = df[["distance", "cum_altitude_gain", "sub_sport", TARGET_NAME]].copy()
    frame["is_trail"] = _sub_sport_to_is_trail(frame["sub_sport"])
    frame = frame.drop(columns=["sub_sport"]).dropna()

    if frame.empty:
        raise ValueError("No valid rows after preprocessing")

    X = frame[list(FEATURE_NAMES)].to_numpy(dtype=float)
    y = frame[TARGET_NAME].to_numpy(dtype=float)

    return FeatureMatrix(
        X=X,
        y=y,
        feature_names=FEATURE_NAMES,
        feature_means=X.mean(axis=0),
    )


def build_inference_vector(
    distance: float,
    cum_altitude_gain: float,
    is_trail: bool,
) -> dict[str, float]:
    return {
        "distance": float(distance),
        "cum_altitude_gain": float(cum_altitude_gain),
        "is_trail": 1.0 if is_trail else 0.0,
    }
