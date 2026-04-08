from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from movie_analysis.data import clean_movie_data, explode_genres, load_sample_dataset, load_uploaded_dataset
from movie_analysis.modeling import predict_single, train_regression_models
from movie_analysis.styles import APP_CSS, hero_card, insight_card, metric_card, section_header

BASE_DIR = Path(__file__).resolve().parent
PALETTE = ["#ff8a3d", "#12c6c2", "#ffd166", "#7bdff2", "#ff5d73", "#8ecae6", "#90be6d", "#c77dff"]

def format_compact_number(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def format_currency(value: float) -> str:
    return f"${format_compact_number(value)}"


def style_figure(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=38, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f7fb", family="Manrope, Aptos, Segoe UI, sans-serif"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.08)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig


def filter_by_genres(frame: pd.DataFrame, selected_genres: list[str]) -> pd.DataFrame:
    if not selected_genres:
        return frame

    selected = set(selected_genres)
    mask = frame["genres"].fillna("").apply(
        lambda value: bool({item.strip() for item in str(value).split(",") if item.strip()} & selected)
    )
    return frame[mask]


def render_metric_row(cards: list[tuple[str, str, str]]) -> None:
    columns = st.columns(len(cards))
    for column, (title, value, detail) in zip(columns, cards):
        with column:
            st.markdown(metric_card(title, value, detail), unsafe_allow_html=True)


def build_missing_chart(cleaning_report: dict[str, object]) -> go.Figure:
    missing_before = cleaning_report["missing_before"]
    missing_after = cleaning_report["missing_after"]
    frame = pd.DataFrame(
        {
            "column": list(missing_before.keys()),
            "Before cleaning": list(missing_before.values()),
            "After cleaning": [missing_after.get(column, 0) for column in missing_before.keys()],
        }
    ).melt(id_vars="column", var_name="stage", value_name="missing_count")

    fig = px.bar(
        frame,
        x="column",
        y="missing_count",
        color="stage",
        barmode="group",
        color_discrete_sequence=[PALETTE[4], PALETTE[1]],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Missing values")
    return style_figure(fig, height=360)


def build_genre_figures(frame: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    genre_frame = explode_genres(frame)
    genre_counts = (
        genre_frame.groupby("genre_item", as_index=False)
        .agg(movie_count=("title", "count"))
        .sort_values(by="movie_count", ascending=True)
    )
    popularity_fig = px.bar(
        genre_counts,
        x="movie_count",
        y="genre_item",
        orientation="h",
        color="movie_count",
        color_continuous_scale=["#11304d", "#ff8a3d"],
    )
    popularity_fig.update_layout(coloraxis_showscale=False, xaxis_title="Movies", yaxis_title="")
    popularity_fig = style_figure(popularity_fig, height=420)

    genre_stats = (
        genre_frame.groupby("genre_item", as_index=False)
        .agg(
            movie_count=("title", "count"),
            avg_rating=("rating", "mean"),
            avg_revenue=("revenue", "mean"),
        )
        .sort_values(by="movie_count", ascending=False)
    )
    genre_stats["avg_revenue_m"] = genre_stats["avg_revenue"] / 1_000_000
    performance_fig = px.scatter(
        genre_stats,
        x="avg_rating",
        y="avg_revenue_m",
        size="movie_count",
        color="genre_item",
        color_discrete_sequence=PALETTE,
        hover_data={"movie_count": True, "avg_revenue_m": ":.2f", "avg_rating": ":.2f"},
    )
    performance_fig.update_layout(xaxis_title="Average rating", yaxis_title="Average revenue (million USD)")
    performance_fig = style_figure(performance_fig, height=420)
    return popularity_fig, performance_fig


def build_rating_revenue_figure(frame: pd.DataFrame) -> tuple[go.Figure, float]:
    scatter_frame = frame[["title", "rating", "revenue", "vote_count", "primary_genre"]].copy()
    scatter_frame["revenue_m"] = scatter_frame["revenue"] / 1_000_000
    scatter_frame["bubble_size"] = np.clip(scatter_frame["vote_count"] / 3200, 12, 52)
    correlation = float(scatter_frame["rating"].corr(scatter_frame["revenue"]))
    if np.isnan(correlation):
        correlation = 0.0

    fig = px.scatter(
        scatter_frame,
        x="rating",
        y="revenue_m",
        color="primary_genre",
        color_discrete_sequence=PALETTE,
        size="bubble_size",
        hover_name="title",
        hover_data={"rating": ":.1f", "revenue_m": ":.2f", "bubble_size": False, "primary_genre": True},
    )

    if len(scatter_frame) >= 3:
        x_line = np.linspace(scatter_frame["rating"].min(), scatter_frame["rating"].max(), 100)
        slope, intercept = np.polyfit(scatter_frame["rating"], scatter_frame["revenue_m"], 1)
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=slope * x_line + intercept,
                mode="lines",
                name="Trend line",
                line=dict(color="#ffd166", width=3),
            )
        )

    fig.update_layout(xaxis_title="Rating", yaxis_title="Revenue (million USD)")
    return style_figure(fig, height=460), correlation


def build_top_movies_figure(frame: pd.DataFrame, metric_column: str, top_n: int) -> tuple[pd.DataFrame, go.Figure]:
    ranking = (
        frame.sort_values(by=metric_column, ascending=False)
        .head(top_n)
        .sort_values(by=metric_column, ascending=True)
        .copy()
    )
    ranking["metric_display"] = ranking[metric_column]
    if metric_column in {"revenue", "budget"}:
        ranking["metric_display"] = ranking[metric_column] / 1_000_000

    fig = px.bar(
        ranking,
        x="metric_display",
        y="title",
        orientation="h",
        color="primary_genre",
        color_discrete_sequence=PALETTE,
        hover_data={"release_year": True, "rating": ":.1f", "metric_display": ":.2f"},
    )
    unit_label = "million USD" if metric_column in {"revenue", "budget"} else metric_column.replace("_", " ").title()
    fig.update_layout(xaxis_title=unit_label, yaxis_title="")
    return ranking, style_figure(fig, height=max(380, top_n * 32))


def build_prediction_scatter(prediction_frame: pd.DataFrame, target_column: str) -> go.Figure:
    unit = "Revenue (USD)" if target_column == "revenue" else "Rating"
    fig = px.scatter(
        prediction_frame,
        x="actual",
        y="predicted",
        color_discrete_sequence=[PALETTE[1]],
        opacity=0.82,
    )
    diagonal = np.linspace(prediction_frame.min().min(), prediction_frame.max().max(), 100)
    fig.add_trace(
        go.Scatter(
            x=diagonal,
            y=diagonal,
            mode="lines",
            name="Ideal line",
            line=dict(color="#ffd166", width=2.5, dash="dash"),
        )
    )
    fig.update_layout(xaxis_title=f"Actual {unit}", yaxis_title=f"Predicted {unit}")
    return style_figure(fig, height=390)


def build_feature_importance_figure(importance_frame: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        importance_frame.sort_values(by="importance", ascending=True),
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale=["#11304d", "#12c6c2"],
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Importance", yaxis_title="")
    return style_figure(fig, height=420)


def main() -> None:
    st.set_page_config(
        page_title="Movie Analysis Dashboard",
        page_icon="MC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.sidebar.markdown("## Control center")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
    numeric_strategy = st.sidebar.selectbox(
        "Numeric missing values",
        options=["median", "mean"],
        format_func=str.title,
    )
    categorical_strategy = st.sidebar.selectbox(
        "Categorical missing values",
        options=["mode", "constant"],
        format_func=lambda value: "Mode" if value == "mode" else "Unknown value",
    )
    drop_duplicates = st.sidebar.toggle("Remove duplicate rows", value=True)
    st.sidebar.caption("Leave the upload empty to use the built-in sample dataset.")

    try:
        if uploaded_file is None:
            raw_df, source_label, dataset_path = load_sample_dataset(BASE_DIR)
            sample_path_label = str(dataset_path.relative_to(BASE_DIR))
        else:
            raw_df, source_label = load_uploaded_dataset(uploaded_file.getvalue(), uploaded_file.name)
            sample_path_label = "Uploaded from local machine"
    except Exception as exc:
        st.error(f"Unable to read the dataset: {exc}")
        return

    cleaned_df, cleaning_report = clean_movie_data(
        raw_df,
        numeric_strategy=numeric_strategy,
        categorical_strategy=categorical_strategy,
        drop_duplicates=drop_duplicates,
    )

    available_genres = sorted(explode_genres(cleaned_df)["genre_item"].dropna().unique().tolist())
    year_min = int(cleaned_df["release_year"].min())
    year_max = int(cleaned_df["release_year"].max())

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Filters")
    selected_years = st.sidebar.slider("Release year range", min_value=year_min, max_value=year_max, value=(year_min, year_max))
    selected_genres = st.sidebar.multiselect("Genres", options=available_genres)

    filtered_df = cleaned_df[cleaned_df["release_year"].between(selected_years[0], selected_years[1])].copy()
    filtered_df = filter_by_genres(filtered_df, selected_genres).reset_index(drop=True)

    if filtered_df.empty:
        st.warning("No rows match the selected filters. Adjust the year range or genre filter.")
        return

    genre_frame = explode_genres(filtered_df)
    genre_counts = genre_frame["genre_item"].value_counts()
    top_genre = genre_counts.index[0] if not genre_counts.empty else "Unknown"
    avg_rating = filtered_df["rating"].mean()
    total_revenue = filtered_df["revenue"].sum()
    average_budget = filtered_df["budget"].mean()
    correlation = filtered_df["rating"].corr(filtered_df["revenue"])
    if pd.isna(correlation):
        correlation = 0.0

    st.markdown(hero_card(source_label, len(filtered_df), len(genre_counts.index)), unsafe_allow_html=True)

    render_metric_row(
        [
            ("Movies in view", format_compact_number(len(filtered_df)), f"Filtered from {len(cleaned_df)} cleaned rows"),
            ("Average rating", f"{avg_rating:.2f}/10", f"Current top genre: {top_genre}"),
            ("Total revenue", format_currency(total_revenue), f"Average budget: {format_currency(average_budget)}"),
            ("Rating vs revenue", f"{correlation:.2f}", "Pearson correlation on current filter"),
        ]
    )

    st.markdown("")
    tabs = st.tabs(
        [
            "Overview",
            "Cleaning",
            "Genres",
            "Rating vs Revenue",
            "Top Movies",
            "Prediction",
            "Data Explorer",
        ]
    )

    with tabs[0]:
        st.markdown(
            section_header(
                "Project overview",
                "A focused view of the current dataset, key findings, and the exact assignment requirements covered by the app.",
            ),
            unsafe_allow_html=True,
        )
        left_col, right_col = st.columns([1.35, 1])
        with left_col:
            st.dataframe(
                filtered_df.head(12),
                width="stretch",
                column_config={
                    "revenue": st.column_config.NumberColumn("Revenue", format="$ %.0f"),
                    "budget": st.column_config.NumberColumn("Budget", format="$ %.0f"),
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
                },
            )
        with right_col:
            st.markdown(
                insight_card(
                    "Data source",
                    f"The dashboard is currently using <strong>{source_label}</strong>. Data file location: <strong>{sample_path_label}</strong>.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Core insight",
                    f"<strong>{top_genre}</strong> appears most often in the filtered data, with an average rating of <strong>{avg_rating:.2f}</strong> and total revenue of <strong>{format_currency(total_revenue)}</strong>.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Assignment checklist",
                    "Missing values are cleaned automatically, genre frequency is tracked, rating and revenue are compared visually, top movies are ranked, and regression models are trained for prediction.",
                ),
                unsafe_allow_html=True,
            )

    with tabs[1]:
        st.markdown(
            section_header(
                "Missing-data cleaning",
                "This section reports missing values before and after cleaning, duplicate removal, and the fill strategy used by the app.",
            ),
            unsafe_allow_html=True,
        )
        render_metric_row(
            [
                ("Rows before cleaning", format_compact_number(cleaning_report["rows_before"]), "Original dataset size"),
                ("Rows after cleaning", format_compact_number(cleaning_report["rows_after"]), "After optional duplicate removal"),
                ("Duplicates removed", format_compact_number(cleaning_report["duplicates_removed"]), "Based on title, year, and studio"),
                ("Columns auto-added", format_compact_number(len(cleaning_report["added_columns"])), "Useful for custom datasets"),
            ]
        )
        missing_chart_col, rules_col = st.columns([1.35, 1])
        with missing_chart_col:
            st.plotly_chart(build_missing_chart(cleaning_report), width="stretch")
        with rules_col:
            numeric_fill_summary = ", ".join(
                f"{column}: {value}" for column, value in cleaning_report["numeric_fill_values"].items()
            )
            categorical_fill_summary = ", ".join(
                f"{column}: {value}" for column, value in cleaning_report["categorical_fill_values"].items()
            )
            st.markdown(
                insight_card(
                    "Cleaning rules",
                    f"Numeric columns use the <strong>{cleaning_report['numeric_strategy']}</strong> strategy. Categorical columns use <strong>{cleaning_report['categorical_strategy']}</strong> filling.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Numeric fill values",
                    numeric_fill_summary,
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Categorical fill values",
                    categorical_fill_summary,
                ),
                unsafe_allow_html=True,
            )

        missing_table = pd.DataFrame(
            {
                "Column": list(cleaning_report["missing_before"].keys()),
                "Before cleaning": list(cleaning_report["missing_before"].values()),
                "After cleaning": [cleaning_report["missing_after"].get(key, 0) for key in cleaning_report["missing_before"].keys()],
            }
        )
        st.dataframe(missing_table, width="stretch")

    with tabs[2]:
        st.markdown(
            section_header(
                "Genre popularity and performance",
                "Genre frequency answers which categories are most common, while the bubble chart compares average rating and average revenue.",
            ),
            unsafe_allow_html=True,
        )
        popularity_fig, performance_fig = build_genre_figures(filtered_df)
        first_col, second_col = st.columns(2)
        with first_col:
            st.plotly_chart(popularity_fig, width="stretch")
        with second_col:
            st.plotly_chart(performance_fig, width="stretch")

        dominant_genre_count = int(genre_counts.iloc[0]) if not genre_counts.empty else 0
        st.markdown(
            insight_card(
                "Genre insight",
                f"<strong>{top_genre}</strong> is the most frequent genre in the current view with <strong>{dominant_genre_count}</strong> movie entries after genre expansion.",
            ),
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown(
            section_header(
                "Relationship between rating and revenue",
                "The scatter plot highlights whether higher-rated movies also tend to earn more revenue in the selected data slice.",
            ),
            unsafe_allow_html=True,
        )
        scatter_fig, scatter_correlation = build_rating_revenue_figure(filtered_df)
        scatter_col, summary_col = st.columns([1.5, 1])
        with scatter_col:
            st.plotly_chart(scatter_fig, width="stretch")
        with summary_col:
            trend_message = "positive" if scatter_correlation >= 0 else "negative"
            strongest_movie = filtered_df.sort_values(by="revenue", ascending=False).iloc[0]
            st.markdown(
                insight_card(
                    "Correlation summary",
                    f"The Pearson correlation is <strong>{scatter_correlation:.2f}</strong>, which indicates a <strong>{trend_message}</strong> relationship between rating and revenue in the filtered data.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Revenue leader",
                    f"<strong>{strongest_movie['title']}</strong> currently leads revenue with <strong>{format_currency(strongest_movie['revenue'])}</strong> and rating <strong>{strongest_movie['rating']:.1f}</strong>.",
                ),
                unsafe_allow_html=True,
            )

    with tabs[4]:
        st.markdown(
            section_header(
                "Top movie visualization",
                "Sort and compare the strongest movies by revenue, rating, or budget. This directly covers the top-movie visualization requirement.",
            ),
            unsafe_allow_html=True,
        )
        control_col1, control_col2 = st.columns([1, 1])
        with control_col1:
            ranking_metric_label = st.selectbox("Ranking metric", options=["Revenue", "Rating", "Budget"], key="ranking_metric")
        with control_col2:
            top_n = st.slider("Number of movies", min_value=5, max_value=20, value=10)

        metric_map = {"Revenue": "revenue", "Rating": "rating", "Budget": "budget"}
        ranking_frame, ranking_fig = build_top_movies_figure(filtered_df, metric_map[ranking_metric_label], top_n)
        chart_col, table_col = st.columns([1.15, 1])
        with chart_col:
            st.plotly_chart(ranking_fig, width="stretch")
        with table_col:
            st.dataframe(
                ranking_frame[["title", "primary_genre", "rating", "revenue", "budget", "release_year"]],
                width="stretch",
                column_config={
                    "title": "Title",
                    "primary_genre": "Main genre",
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
                    "revenue": st.column_config.NumberColumn("Revenue", format="$ %.0f"),
                    "budget": st.column_config.NumberColumn("Budget", format="$ %.0f"),
                },
            )

    with tabs[5]:
        st.markdown(
            section_header(
                "Prediction model",
                "Train multiple regression models, compare their performance, and run a custom prediction for revenue or rating.",
            ),
            unsafe_allow_html=True,
        )
        target_label = st.selectbox("Prediction target", options=["Revenue", "Rating"], key="prediction_target")
        target_column = "revenue" if target_label == "Revenue" else "rating"
        st.caption("The model trains on the current filter, so changing years or genres updates the prediction context.")

        try:
            model_bundle = train_regression_models(filtered_df, target_column=target_column)
        except ValueError as exc:
            st.warning(str(exc))
        else:
            top_model_row = model_bundle["leaderboard"].iloc[0]
            render_metric_row(
                [
                    ("Best model", model_bundle["best_model_name"], f"Train: {model_bundle['train_size']} rows"),
                    ("R2 score", f"{top_model_row['R2']:.3f}", "Closer to 1 means stronger fit"),
                    ("RMSE", format_currency(top_model_row["RMSE"]) if target_column == "revenue" else f"{top_model_row['RMSE']:.2f}", "Prediction error"),
                    ("MAE", format_currency(top_model_row["MAE"]) if target_column == "revenue" else f"{top_model_row['MAE']:.2f}", "Average absolute error"),
                ]
            )

            leaderboard_display = model_bundle["leaderboard"].copy()
            st.dataframe(
                leaderboard_display,
                width="stretch",
                column_config={
                    "MAE": st.column_config.NumberColumn("MAE", format="%.3f"),
                    "RMSE": st.column_config.NumberColumn("RMSE", format="%.3f"),
                    "R2": st.column_config.NumberColumn("R2", format="%.3f"),
                },
            )

            importance_col, prediction_col = st.columns(2)
            with importance_col:
                st.plotly_chart(build_feature_importance_figure(model_bundle["feature_importance"]), width="stretch")
            with prediction_col:
                st.plotly_chart(
                    build_prediction_scatter(model_bundle["prediction_frame"], target_column=target_column),
                    width="stretch",
                )

            st.markdown(
                section_header(
                    "Custom prediction",
                    "Enter a movie profile below to estimate the selected target using the best model.",
                ),
                unsafe_allow_html=True,
            )

            genre_options = sorted(filtered_df["primary_genre"].dropna().astype(str).unique().tolist())
            studio_options = sorted(filtered_df["studio"].dropna().astype(str).unique().tolist())
            language_options = sorted(filtered_df["language"].dropna().astype(str).unique().tolist())

            with st.form("prediction_form"):
                col1, col2, col3, col4 = st.columns(4)
                budget = col1.number_input(
                    "Budget (USD)",
                    min_value=1_000_000.0,
                    value=float(filtered_df["budget"].median()),
                    step=5_000_000.0,
                )
                runtime = col2.number_input(
                    "Runtime (minutes)",
                    min_value=60,
                    max_value=220,
                    value=int(filtered_df["runtime"].median()),
                    step=1,
                )
                release_year = col3.slider(
                    "Release year",
                    min_value=int(cleaned_df["release_year"].min()),
                    max_value=int(cleaned_df["release_year"].max()) + 2,
                    value=int(filtered_df["release_year"].median()),
                )
                vote_count = col4.number_input(
                    "Vote count",
                    min_value=0,
                    value=int(filtered_df["vote_count"].median()),
                    step=1000,
                )
                col5, col6, col7 = st.columns(3)
                metascore = col5.slider("Metascore", min_value=0, max_value=100, value=int(filtered_df["metascore"].median()))
                primary_genre = col6.selectbox("Main genre", options=genre_options, index=0)
                studio = col7.selectbox("Studio", options=studio_options, index=0)
                language = st.selectbox("Language", options=language_options, index=0)
                submitted = st.form_submit_button("Run prediction")

            if submitted:
                payload = {
                    "budget": budget,
                    "runtime": runtime,
                    "release_year": release_year,
                    "vote_count": vote_count,
                    "metascore": metascore,
                    "primary_genre": primary_genre,
                    "studio": studio,
                    "language": language,
                }
                prediction = predict_single(model_bundle, payload, target_column=target_column)
                if target_column == "revenue":
                    st.success(f"Predicted revenue: {format_currency(prediction)}")
                else:
                    st.success(f"Predicted rating: {prediction:.2f}/10")

    with tabs[6]:
        st.markdown(
            section_header(
                "Data explorer and export",
                "Inspect both raw and cleaned datasets, then download the processed data for reporting or further analysis.",
            ),
            unsafe_allow_html=True,
        )
        raw_col, clean_col = st.columns(2)
        with raw_col:
            st.markdown("### Raw dataset")
            st.dataframe(raw_df.head(12), width="stretch")
        with clean_col:
            st.markdown("### Cleaned dataset")
            st.dataframe(cleaned_df.head(12), width="stretch")

        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.download_button(
                "Download cleaned CSV",
                data=cleaned_df.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_movie_dataset.csv",
                mime="text/csv",
            )
        with export_col2:
            st.download_button(
                "Download filtered CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_movie_dataset.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    if get_script_run_ctx() is None:
        print("This is a Streamlit app. Run it with:")
        print(r"  ..\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false")
        print("Or double-click run_app.bat / run_app.ps1.")
        sys.exit(0)
    main()
