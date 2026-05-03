from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .data import build_data_quality_report, clean_movie_data, load_sample_dataset, load_uploaded_dataset


@dataclass(frozen=True)
class DatasetBundle:
    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    source_label: str
    sample_path_label: str
    cleaning_report: dict[str, Any]
    quality_report: dict[str, Any]


def prepare_dataset_bundle(
    *,
    base_dir: Path,
    uploaded_file_bytes: bytes | None,
    uploaded_filename: str | None,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    drop_duplicates: bool = True,
) -> DatasetBundle:
    """
    End-to-end data processing pipeline for the whole app.

    Input:
    - Either an uploaded dataset (bytes + filename) or None to use the internal sample dataset.

    Output:
    - Raw dataframe
    - Cleaned dataframe (normalized columns, missing handled, duplicates optional, engineered fields)
    - Cleaning report + quality report
    - Source labels used by the UI
    """
    if uploaded_file_bytes is None or uploaded_filename is None:
        raw_df, source_label, dataset_path = load_sample_dataset(base_dir)
        sample_path_label = str(dataset_path.relative_to(base_dir))
    else:
        raw_df, source_label = load_uploaded_dataset(uploaded_file_bytes, uploaded_filename)
        sample_path_label = "Uploaded from local machine"

    cleaned_df, cleaning_report = clean_movie_data(
        raw_df,
        numeric_strategy=numeric_strategy,
        categorical_strategy=categorical_strategy,
        drop_duplicates=drop_duplicates,
    )
    quality_report = build_data_quality_report(raw_df, cleaned_df)

    return DatasetBundle(
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        source_label=source_label,
        sample_path_label=sample_path_label,
        cleaning_report=cleaning_report,
        quality_report=quality_report,
    )

