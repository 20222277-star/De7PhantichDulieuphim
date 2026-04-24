from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DATA_DIR_NAME = "sample_data"
DATASET_FILE_NAME = "movies_analysis_dataset.csv"

NUMERIC_COLUMNS = [
    "rating",
    "revenue",
    "budget",
    "runtime",
    "release_year",
    "vote_count",
    "metascore",
]
DERIVED_NUMERIC_COLUMNS = ["profit", "roi"]
CATEGORICAL_COLUMNS = ["title", "genres", "studio", "language"]
REQUIRED_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
DEFAULT_NUMERIC_VALUES = {
    "rating": 6.8,
    "revenue": 135_000_000.0,
    "budget": 58_000_000.0,
    "runtime": 112.0,
    "release_year": 2019.0,
    "vote_count": 78_000.0,
    "metascore": 67.0,
}
COLUMN_ALIASES = {
    "title": {"title", "movie_title", "name", "movie", "film", "movie_name"},
    "genres": {"genres", "genre", "category", "categories", "the_loai", "loai_phim"},
    "rating": {"rating", "vote_average", "imdb_rating", "score", "diem"},
    "revenue": {"revenue", "box_office", "gross", "doanh_thu"},
    "budget": {"budget", "production_budget", "ngan_sach"},
    "runtime": {"runtime", "duration", "length", "thoi_luong"},
    "release_year": {"release_year", "year", "nam_phat_hanh", "release"},
    "vote_count": {"vote_count", "votes", "num_votes", "luot_danh_gia"},
    "metascore": {"metascore", "critic_score", "review_score", "diem_phe_binh"},
    "studio": {"studio", "production_company", "company", "hang_phim"},
    "language": {"language", "original_language", "ngon_ngu"},
}


def _slugify_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def normalize_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    renamed = frame.copy()
    added_columns: list[str] = []
    rename_map: dict[str, str] = {}

    for column in renamed.columns:
        slug = _slugify_column(column)
        for canonical, aliases in COLUMN_ALIASES.items():
            if slug in aliases:
                rename_map[column] = canonical
                break

    renamed = renamed.rename(columns=rename_map)

    if "release_date" in renamed.columns and "release_year" not in renamed.columns:
        renamed["release_year"] = pd.to_datetime(renamed["release_date"], errors="coerce").dt.year

    for column in REQUIRED_COLUMNS:
        if column not in renamed.columns:
            renamed[column] = pd.NA
            added_columns.append(column)

    ordered_columns = REQUIRED_COLUMNS + [column for column in renamed.columns if column not in REQUIRED_COLUMNS]
    return renamed[ordered_columns], added_columns


def _normalize_genre_value(value: Any) -> str:
    if pd.isna(value):
        return ""

    text = str(value)
    text = re.sub(r"[\[\]\'\"]", "", text)
    parts = re.split(r"[|,;/]+", text)
    cleaned: list[str] = []

    for part in parts:
        genre = re.sub(r"\s+", " ", part).strip()
        if not genre:
            continue
        genre = genre.title()
        if genre not in cleaned:
            cleaned.append(genre)

    return ", ".join(cleaned)


def _build_movie_title(index: int, rng: np.random.Generator) -> str:
    adjectives = [
        "Hidden",
        "Electric",
        "Golden",
        "Burning",
        "Crystal",
        "Neon",
        "Silent",
        "Last",
        "Midnight",
        "Velvet",
        "Scarlet",
        "Shadow",
        "Brave",
        "Broken",
        "Silver",
        "Wild",
        "Fallen",
        "Infinite",
    ]
    nouns = [
        "Signal",
        "Empire",
        "Voyage",
        "Season",
        "Harbor",
        "City",
        "Pulse",
        "Labyrinth",
        "Mirage",
        "Archive",
        "Circuit",
        "Legacy",
        "Frontier",
        "Echo",
        "Storm",
        "Orbit",
        "Formula",
        "Kingdom",
    ]
    suffix = rng.choice(["", "", "", " II", " Rising", " Returns", " Reborn"])
    return f"{rng.choice(adjectives)} {rng.choice(nouns)} {index:03d}{suffix}"


def generate_movie_dataset(rows: int = 320, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    genre_profiles = {
        "Action": {"budget": 125, "rating": 6.9, "multiplier": 3.2, "runtime": 128},
        "Adventure": {"budget": 110, "rating": 7.1, "multiplier": 3.0, "runtime": 122},
        "Animation": {"budget": 88, "rating": 7.4, "multiplier": 2.8, "runtime": 101},
        "Comedy": {"budget": 45, "rating": 6.6, "multiplier": 2.2, "runtime": 108},
        "Crime": {"budget": 55, "rating": 7.2, "multiplier": 2.0, "runtime": 116},
        "Drama": {"budget": 38, "rating": 7.4, "multiplier": 1.9, "runtime": 118},
        "Fantasy": {"budget": 95, "rating": 7.0, "multiplier": 2.7, "runtime": 121},
        "Horror": {"budget": 22, "rating": 6.3, "multiplier": 2.6, "runtime": 97},
        "Romance": {"budget": 30, "rating": 6.9, "multiplier": 1.8, "runtime": 110},
        "Sci-Fi": {"budget": 118, "rating": 7.2, "multiplier": 3.1, "runtime": 124},
        "Thriller": {"budget": 52, "rating": 6.8, "multiplier": 2.3, "runtime": 111},
    }
    genre_names = list(genre_profiles.keys())
    genre_weights = np.array([0.14, 0.09, 0.07, 0.13, 0.09, 0.15, 0.07, 0.08, 0.06, 0.06, 0.06])
    studios = [
        "Atlas Vision",
        "Blue Harbor",
        "Northlight",
        "Silverline",
        "Solaris Pictures",
        "Maple Frame",
        "EchoWorks",
        "Vista Peak",
        "Aurora Motion",
        "Twin Lantern",
    ]
    languages = ["English", "Korean", "Japanese", "French", "Spanish", "Vietnamese"]

    records: list[dict[str, Any]] = []

    for index in range(1, rows + 1):
        genre_count = int(rng.choice([1, 2, 3], p=[0.56, 0.31, 0.13]))
        genres = list(rng.choice(genre_names, size=genre_count, replace=False, p=genre_weights))
        profile_values = [genre_profiles[genre] for genre in genres]

        budget_millions = max(8.0, rng.normal(np.mean([item["budget"] for item in profile_values]), 18.0))
        rating = float(np.clip(rng.normal(np.mean([item["rating"] for item in profile_values]), 0.55), 4.8, 9.3))
        runtime = int(np.clip(rng.normal(np.mean([item["runtime"] for item in profile_values]), 13.0), 82, 185))
        vote_count = int(
            max(
                600,
                rng.lognormal(mean=np.log(60_000 + budget_millions * 1_500), sigma=0.48),
            )
        )
        release_year = int(rng.integers(2008, 2026))
        metascore = int(np.clip(rng.normal(rating * 9.6 + 2.0, 6.0), 35, 95))

        release_boost = 1.0 + max(release_year - 2016, 0) * 0.016
        genre_multiplier = np.mean([item["multiplier"] for item in profile_values])
        buzz_factor = 0.85 + np.log10(vote_count) * 0.18
        rating_factor = 0.82 + (rating - 5.5) * 0.19
        random_factor = float(np.clip(rng.normal(1.0, 0.18), 0.65, 1.55))
        revenue = budget_millions * 1_000_000 * genre_multiplier * buzz_factor * rating_factor * release_boost * random_factor
        revenue = max(revenue, budget_millions * 1_000_000 * 0.72)

        records.append(
            {
                "title": _build_movie_title(index, rng),
                "genres": ", ".join(genres),
                "rating": round(rating, 1),
                "revenue": round(float(revenue), 2),
                "budget": round(budget_millions * 1_000_000, 2),
                "runtime": runtime,
                "release_year": release_year,
                "vote_count": vote_count,
                "metascore": metascore,
                "studio": str(rng.choice(studios)),
                "language": str(rng.choice(languages, p=[0.62, 0.09, 0.08, 0.08, 0.07, 0.06])),
            }
        )

    dataset = pd.DataFrame.from_records(records)

    missing_rates = {
        "rating": 0.05,
        "revenue": 0.04,
        "budget": 0.05,
        "runtime": 0.03,
        "genres": 0.03,
        "studio": 0.04,
        "metascore": 0.06,
    }
    for column, rate in missing_rates.items():
        sample_size = max(1, int(len(dataset) * rate))
        indices = rng.choice(dataset.index, size=sample_size, replace=False)
        dataset.loc[indices, column] = np.nan

    duplicate_indices = rng.choice(dataset.index, size=8, replace=False)
    dataset = pd.concat([dataset, dataset.loc[duplicate_indices]], ignore_index=True)
    return dataset


def ensure_sample_dataset(base_dir: Path) -> Path:
    data_dir = base_dir / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = data_dir / DATASET_FILE_NAME

    if not dataset_path.exists():
        sample_data = generate_movie_dataset()
        sample_data.to_csv(dataset_path, index=False)

    return dataset_path


def load_sample_dataset(base_dir: Path) -> tuple[pd.DataFrame, str, Path]:
    dataset_path = ensure_sample_dataset(base_dir)
    dataset = pd.read_csv(dataset_path)
    return dataset, "Internal generated movie dataset", dataset_path


def load_uploaded_dataset(file_bytes: bytes, filename: str) -> tuple[pd.DataFrame, str]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        dataset = pd.read_csv(BytesIO(file_bytes))
    elif suffix in {".xlsx", ".xls"}:
        dataset = pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file type. Please upload CSV or Excel.")

    return dataset, f"Uploaded file: {filename}"


def clean_movie_data(
    frame: pd.DataFrame,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    drop_duplicates: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    working, added_columns = normalize_columns(frame)
    working = working.copy()
    rows_before = len(working)

    before_missing_frame = working[REQUIRED_COLUMNS].copy()
    before_missing_frame["genres"] = before_missing_frame["genres"].replace(r"^\s*$", pd.NA, regex=True)

    for column in NUMERIC_COLUMNS:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working["genres"] = working["genres"].apply(_normalize_genre_value)
    before_missing = before_missing_frame.isna().sum().to_dict()

    duplicate_columns = [column for column in ["title", "release_year", "studio"] if column in working.columns]
    duplicates_removed = 0
    if drop_duplicates and duplicate_columns:
        duplicates_removed = int(working.duplicated(subset=duplicate_columns, keep="first").sum())
        working = working.drop_duplicates(subset=duplicate_columns, keep="first")

    numeric_fill_values: dict[str, float] = {}
    for column in NUMERIC_COLUMNS:
        non_null = working[column].dropna()
        if non_null.empty:
            fill_value = DEFAULT_NUMERIC_VALUES[column]
        elif numeric_strategy == "mean":
            fill_value = float(non_null.mean())
        else:
            fill_value = float(non_null.median())

        working[column] = working[column].fillna(fill_value)
        numeric_fill_values[column] = round(fill_value, 2)

    categorical_fill_values: dict[str, str] = {}
    for column in CATEGORICAL_COLUMNS:
        working[column] = working[column].astype("string").str.strip()
        working[column] = working[column].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        if column == "title":
            fill_value = "Untitled Film"
        elif categorical_strategy == "constant":
            fill_value = "Unknown"
        else:
            non_null = working[column].dropna()
            fill_value = str(non_null.mode().iloc[0]) if not non_null.empty else "Unknown"

        working[column] = working[column].fillna(fill_value)
        categorical_fill_values[column] = fill_value

    working["primary_genre"] = working["genres"].str.split(",").str[0].str.strip().fillna("Unknown")
    working["runtime"] = working["runtime"].round().clip(lower=60, upper=220).astype(int)
    working["release_year"] = working["release_year"].round().clip(lower=1980, upper=2030).astype(int)
    working["vote_count"] = working["vote_count"].round().clip(lower=0).astype(int)
    working["metascore"] = working["metascore"].round().clip(lower=0, upper=100).astype(int)
    working["rating"] = working["rating"].clip(lower=0, upper=10)
    working["budget"] = working["budget"].clip(lower=1_000_000)
    working["revenue"] = working["revenue"].clip(lower=1_000_000)
    working["profit"] = working["revenue"] - working["budget"]
    working["roi"] = np.where(working["budget"] > 0, working["revenue"] / working["budget"], np.nan)

    after_missing = working[REQUIRED_COLUMNS + ["primary_genre"]].isna().sum().to_dict()
    report = {
        "rows_before": rows_before,
        "rows_after": len(working),
        "duplicates_removed": duplicates_removed,
        "missing_before": before_missing,
        "missing_after": after_missing,
        "numeric_strategy": numeric_strategy,
        "categorical_strategy": categorical_strategy,
        "numeric_fill_values": numeric_fill_values,
        "categorical_fill_values": categorical_fill_values,
        "added_columns": added_columns,
    }
    return working.reset_index(drop=True), report


def explode_genres(frame: pd.DataFrame) -> pd.DataFrame:
    expanded = frame.copy()
    expanded["genre_item"] = expanded["genres"].fillna("Unknown").str.split(",")
    expanded = expanded.explode("genre_item")
    expanded["genre_item"] = expanded["genre_item"].astype("string").str.strip()
    expanded["genre_item"] = expanded["genre_item"].replace({"": "Unknown", "<NA>": "Unknown"})
    return expanded


def build_data_quality_report(raw_frame: pd.DataFrame, cleaned_frame: pd.DataFrame) -> dict[str, Any]:
    cleaned_numeric_columns = [column for column in NUMERIC_COLUMNS + DERIVED_NUMERIC_COLUMNS if column in cleaned_frame.columns]
    raw_numeric_columns = [column for column in NUMERIC_COLUMNS if column in raw_frame.columns]

    completeness_rows: list[dict[str, Any]] = []
    for column in REQUIRED_COLUMNS:
        if column in raw_frame.columns:
            missing_count = int(raw_frame[column].isna().sum())
            missing_pct = float(raw_frame[column].isna().mean() * 100)
        else:
            missing_count = len(raw_frame)
            missing_pct = 100.0
        completeness_rows.append(
            {
                "column": column,
                "missing_count": missing_count,
                "missing_pct": missing_pct,
            }
        )

    outlier_rows: list[dict[str, Any]] = []
    for column in cleaned_numeric_columns:
        series = pd.to_numeric(cleaned_frame[column], errors="coerce").dropna()
        if len(series) < 4:
            outlier_count = 0
        else:
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            if iqr == 0:
                outlier_count = 0
            else:
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outlier_count = int(((series < lower_bound) | (series > upper_bound)).sum())

        outlier_rows.append(
            {
                "column": column,
                "outlier_count": outlier_count,
                "outlier_pct": float((outlier_count / max(len(cleaned_frame), 1)) * 100),
            }
        )

    invalid_rows: list[dict[str, Any]] = []
    invalid_rules = {
        "rating_out_of_range": ("rating", lambda series: (series < 0) | (series > 10)),
        "negative_revenue": ("revenue", lambda series: series < 0),
        "negative_budget": ("budget", lambda series: series < 0),
        "runtime_too_short": ("runtime", lambda series: series < 40),
        "release_year_out_of_range": ("release_year", lambda series: (series < 1900) | (series > 2035)),
        "negative_vote_count": ("vote_count", lambda series: series < 0),
        "metascore_out_of_range": ("metascore", lambda series: (series < 0) | (series > 100)),
    }
    for rule_name, (column, validator) in invalid_rules.items():
        if column not in raw_frame.columns:
            continue
        series = pd.to_numeric(raw_frame[column], errors="coerce")
        invalid_count = int(validator(series.fillna(np.nan)).sum())
        invalid_rows.append({"rule": rule_name, "column": column, "invalid_count": invalid_count})

    duplicate_count = int(raw_frame.duplicated().sum())
    completeness_frame = pd.DataFrame(completeness_rows).sort_values(by="missing_pct", ascending=False).reset_index(drop=True)
    outlier_frame = pd.DataFrame(outlier_rows).sort_values(by="outlier_count", ascending=False).reset_index(drop=True)
    invalid_frame = pd.DataFrame(invalid_rows).sort_values(by="invalid_count", ascending=False).reset_index(drop=True)

    return {
        "duplicate_rows_raw": duplicate_count,
        "completeness": completeness_frame,
        "outliers": outlier_frame,
        "invalids": invalid_frame,
        "raw_row_count": len(raw_frame),
        "cleaned_row_count": len(cleaned_frame),
    }
