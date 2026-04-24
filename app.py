from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from movie_analysis.data import (
    build_data_quality_report,
    clean_movie_data,
    explode_genres,
    load_sample_dataset,
    load_uploaded_dataset,
)
from movie_analysis.modeling import predict_single, train_regression_models
from movie_analysis.styles import APP_CSS, hero_card, insight_card, metric_card, section_header

BASE_DIR = Path(__file__).resolve().parent
PALETTE = ["#ff8a3d", "#12c6c2", "#ffd166", "#7bdff2", "#ff5d73", "#8ecae6", "#90be6d", "#c77dff"]
LANGUAGE_OPTIONS = {"Tiếng Việt": "vi", "English": "en"}
TRANSLATIONS = {
    "vi": {
        "app_title": "Phân Tích Dữ Liệu Phim",
        "sidebar_control": "## Trung tâm điều khiển",
        "language": "Ngôn ngữ",
        "upload": "Tải lên file CSV hoặc Excel",
        "numeric_missing": "Xử lý dữ liệu số bị thiếu",
        "categorical_missing": "Xử lý dữ liệu chữ bị thiếu",
        "mode": "Mode",
        "unknown_value": "Giá trị không xác định",
        "remove_duplicates": "Xóa dòng trùng lặp",
        "leave_upload_empty": "Để trống phần tải file nếu muốn dùng bộ dữ liệu nội bộ do project tạo.",
        "unable_read_dataset": "Không thể đọc bộ dữ liệu: {exc}",
        "uploaded_from_local": "Tải lên từ máy cục bộ",
        "filters": "## Bộ lọc",
        "release_year_range": "Khoảng năm phát hành",
        "genres": "Thể loại",
        "no_rows_match": "Không có dòng dữ liệu nào khớp với bộ lọc hiện tại. Hãy đổi lại khoảng năm hoặc thể loại.",
        "hero_eyebrow": "Phòng Phân Tích Phim",
        "hero_title": "Dashboard phân tích phim cho làm sạch dữ liệu, insight và dự đoán",
        "hero_desc": "Ứng dụng đáp ứng các yêu cầu chính của đề tài: làm sạch dữ liệu thiếu, phân tích thể loại, phân tích rating và doanh thu, trực quan hóa top phim, và dự đoán doanh thu, rating hoặc lượt xem.",
        "source": "Nguồn dữ liệu",
        "rows": "Số dòng",
        "movies": "Số phim",
        "movies_in_view": "Phim đang xem",
        "filtered_from_rows": "Lọc từ {count} dòng đã làm sạch",
        "average_rating": "Rating trung bình",
        "current_top_genre": "Thể loại nổi bật: {genre}",
        "total_revenue": "Tổng doanh thu",
        "average_profit": "Lợi nhuận TB: {value}",
        "average_views": "Lượt xem trung bình",
        "based_on_vote_count": "Dựa trên vote_count của tập đang xem",
        "tab_overview": "Tổng quan",
        "tab_cleaning": "Làm sạch",
        "tab_data_quality": "Chất lượng dữ liệu",
        "tab_genres": "Thể loại",
        "tab_compare": "So sánh",
        "tab_time_trends": "Xu hướng thời gian",
        "tab_distribution": "Phân phối",
        "tab_rating_revenue": "Rating và Doanh thu",
        "tab_top_movies": "Top phim",
        "tab_movie_detail": "Chi tiết phim",
        "tab_prediction": "Dự đoán",
        "tab_data_explorer": "Khám phá dữ liệu",
        "data_explorer": "Khám phá dữ liệu và xuất file",
        "view_count": "Lượt xem",
        "uploaded_file_prefix": "File tải lên: {filename}",
        "raw_dataset": "Dữ liệu gốc",
        "cleaned_dataset": "Dữ liệu đã làm sạch",
        "download_cleaned_csv": "Tải CSV đã làm sạch",
        "download_filtered_csv": "Tải CSV đã lọc",
        "run_prediction": "Chạy dự đoán",
        "budget_usd": "Ngân sách (USD)",
        "runtime_minutes": "Thời lượng (phút)",
        "release_year": "Năm phát hành",
        "current_view_count": "Lượt xem hiện tại / vote_count",
        "main_genre": "Thể loại chính",
        "studio": "Hãng phim",
        "language_label": "Ngôn ngữ",
        "choose_movie": "Chọn một phim",
        "peer_movies": "Các phim tương đồng",
        "prediction_target": "Mục tiêu dự đoán",
        "revenue": "Doanh thu",
        "rating": "Rating",
        "budget": "Ngân sách",
        "profit": "Lợi nhuận",
        "roi": "ROI",
        "movie_count": "Số phim",
        "compare_by": "So sánh theo",
        "genre": "Thể loại",
        "select_exactly_two": "Chọn đúng 2 {label}",
        "choose_exactly_two": "Hãy chọn đúng 2 {label} để mở chế độ so sánh.",
        "comparison_metric": "Chỉ số so sánh",
        "trend_metric": "Chỉ số xu hướng",
        "distribution_metric": "Chỉ số phân phối",
        "ranking_metric": "Tiêu chí xếp hạng",
        "number_of_movies": "Số lượng phim",
        "best_model": "Mô hình tốt nhất",
        "train_rows": "Train: {count} dòng",
        "r2_score": "Điểm R2",
        "closer_to_1": "Càng gần 1 càng tốt",
        "prediction_error": "Sai số dự đoán",
        "average_absolute_error": "Sai số tuyệt đối TB",
        "predicted_target": "Giá trị dự đoán",
        "predicted_view_count": "Lượt xem dự đoán",
        "expected_trend": "Xu hướng kỳ vọng",
        "most_watched_movie": "Phim xem nhiều nhất",
        "least_watched_movie": "Phim xem ít nhất",
        "predicted_movie": "Phim được dự đoán",
        "custom_input_movie": "Phim nhập tay",
        "type": "Loại",
        "title": "Tên phim",
        "views": "Lượt xem",
        "scenario_analysis": "Phân tích kịch bản",
        "predicted_value": "Giá trị dự đoán",
        "predicted_revenue": "Doanh thu dự đoán",
        "predicted_rating": "Rating dự đoán",
        "predicted_view_count_label": "Lượt xem dự đoán",
        "this_is_streamlit_app": "Đây là ứng dụng Streamlit. Hãy chạy bằng:",
        "or_double_click": "Hoặc nhấp đúp vào run_app.bat / run_app.ps1.",
        "before_cleaning": "Trước khi làm sạch",
        "after_cleaning": "Sau khi làm sạch",
        "missing_values": "Giá trị thiếu",
        "cleaning_section_title": "Làm sạch dữ liệu thiếu",
        "cleaning_section_caption": "Phần này báo cáo dữ liệu thiếu trước và sau khi làm sạch, số dòng trùng lặp bị xóa và quy tắc điền dữ liệu.",
        "rows_before_cleaning": "Số dòng trước làm sạch",
        "rows_after_cleaning": "Số dòng sau làm sạch",
        "original_dataset_size": "Kích thước dữ liệu gốc",
        "after_optional_duplicate_removal": "Sau khi xóa trùng lặp nếu bật tùy chọn",
        "duplicates_removed": "Số dòng trùng lặp đã xóa",
        "based_on_title_year_studio": "Dựa trên title, year và studio",
        "columns_auto_added": "Số cột tự bổ sung",
        "useful_for_custom_datasets": "Hữu ích với dữ liệu tự tải lên",
        "cleaning_rules": "Quy tắc làm sạch",
        "numeric_fill_values": "Giá trị điền số",
        "categorical_fill_values": "Giá trị điền chữ",
        "numeric_columns_use_strategy": "Các cột số dùng chiến lược <strong>{numeric}</strong>. Các cột chữ dùng cách điền <strong>{categorical}</strong>.",
        "data_quality_title": "Kiểm tra chất lượng dữ liệu",
        "data_quality_caption": "Phân tích missing rate, outlier, duplicate và giá trị không hợp lệ trước khi tin vào insight hoặc mô hình.",
        "raw_rows": "Số dòng gốc",
        "cleaned_rows": "Số dòng sau xử lý",
        "raw_duplicates": "Số dòng trùng gốc",
        "exact_duplicated_rows": "Số dòng trùng hoàn toàn",
        "worst_missing_column": "Cột thiếu nhiều nhất",
        "no_invalid_values": "Không phát hiện giá trị số không hợp lệ trong dữ liệu gốc đã tải lên.",
        "genres_title": "Mức độ phổ biến và hiệu suất thể loại",
        "genres_caption": "Biểu đồ tần suất cho biết thể loại nào phổ biến nhất, còn biểu đồ bong bóng so sánh rating và doanh thu trung bình.",
        "genre_insight": "Insight thể loại",
        "genre_insight_body": "<strong>{genre}</strong> là thể loại xuất hiện nhiều nhất trong vùng dữ liệu hiện tại với <strong>{count}</strong> phim sau khi tách thể loại.",
        "compare_title": "Phân tích so sánh",
        "compare_caption": "So sánh trực tiếp 2 thể loại hoặc 2 hãng phim theo số phim, rating, doanh thu, lợi nhuận, ROI và lượt xem.",
        "comparison_insight": "Insight so sánh",
        "comparison_insight_body": "<strong>{winner}</strong> đang dẫn đầu ở chỉ số <strong>{metric}</strong> với khoảng cách <strong>{gap}</strong> so với <strong>{runner}</strong>.",
        "time_trends_title": "Xu hướng theo thời gian",
        "time_trends_caption": "Theo dõi số lượng phim, rating, doanh thu, lợi nhuận và ROI theo năm phát hành để nhìn ra bức tranh toàn cục.",
        "year_highlights": "Điểm nổi bật theo năm",
        "year_highlights_body": "Năm có ROI mạnh nhất là <strong>{best_year}</strong> với <strong>{best_roi:.2f}x</strong>. Năm có tổng doanh thu lớn nhất là <strong>{market_year}</strong> với <strong>{market_revenue}</strong>.",
        "distribution_title": "Phân phối và tương quan",
        "distribution_caption": "Xem độ phân tán, độ lệch và các mối tương quan giữa biến số thay vì chỉ phân tích một cặp biến.",
        "rating_revenue_title": "Mối quan hệ giữa rating và doanh thu",
        "rating_revenue_caption": "Biểu đồ phân tán cho thấy phim rating cao có xu hướng doanh thu cao hơn hay không trong tập dữ liệu đã lọc.",
        "positive": "dương",
        "negative": "âm",
        "correlation_summary": "Tóm tắt tương quan",
        "correlation_summary_body": "Hệ số tương quan Pearson là <strong>{corr:.2f}</strong>, cho thấy mối quan hệ <strong>{trend}</strong> giữa rating và doanh thu trong tập đã lọc.",
        "revenue_leader": "Phim dẫn đầu doanh thu",
        "revenue_leader_body": "<strong>{title}</strong> hiện dẫn đầu doanh thu với <strong>{revenue}</strong> và rating <strong>{rating:.1f}</strong>.",
        "top_movies_title": "Trực quan hóa top phim",
        "top_movies_caption": "Sắp xếp và so sánh các phim mạnh nhất theo doanh thu, rating, ngân sách, lợi nhuận hoặc ROI.",
        "main_genre_col": "Thể loại chính",
        "movie_detail_title": "Phân tích chi tiết từng phim",
        "movie_detail_caption": "Chọn một phim và benchmark nó với toàn bộ tập dữ liệu, thể loại, hãng phim và các phim cùng giai đoạn phát hành.",
        "selected_rating": "Rating đã chọn",
        "selected_revenue": "Doanh thu đã chọn",
        "selected_profit": "Lợi nhuận đã chọn",
        "genre_prefix": "Thể loại: {genre}",
        "budget_prefix": "Ngân sách: {value}",
        "roi_prefix": "ROI: {value:.2f}x",
        "studio_prefix": "Hãng phim: {studio}",
        "movie_summary": "Tóm tắt phim",
        "movie_summary_body": "<strong>{title}</strong> phát hành năm <strong>{year}</strong>. Phim thuộc thể loại <strong>{genre}</strong>, đạt doanh thu <strong>{revenue}</strong> từ ngân sách <strong>{budget}</strong> và mang lại ROI <strong>{roi:.2f}x</strong>.",
        "benchmarks": "Mốc so sánh",
        "benchmarks_body": "Rating của phim chênh <strong>{rating_gap:+.2f}</strong> so với trung bình thể loại, còn lượt xem chênh <strong>{views_gap:+,}</strong> so với trung bình hãng phim.",
        "prediction_title": "Mô hình dự đoán",
        "prediction_caption": "Huấn luyện nhiều mô hình hồi quy, so sánh hiệu năng và dự đoán doanh thu, rating hoặc lượt xem.",
        "prediction_context": "Mô hình được huấn luyện trên tập đã lọc hiện tại, nên việc đổi năm hoặc thể loại sẽ làm thay đổi bối cảnh dự đoán.",
        "custom_prediction_title": "Dự đoán tùy chỉnh",
        "custom_prediction_caption": "Nhập hồ sơ phim để ước lượng mục tiêu đã chọn, xu hướng lượt xem và vị trí độ phổ biến so với dữ liệu hiện tại.",
        "scenario_caption": "Biểu đồ này thay đổi ngân sách nhưng giữ nguyên các thuộc tính còn lại để cho thấy dự đoán nhạy với đầu tư đến mức nào.",
        "data_explorer_caption": "Xem đồng thời dữ liệu gốc và dữ liệu đã làm sạch, sau đó tải dữ liệu đã xử lý để phục vụ báo cáo hoặc phân tích tiếp.",
    },
    "en": {
        "app_title": "Movie Analysis Dashboard",
        "sidebar_control": "## Control center",
        "language": "Language",
        "upload": "Upload CSV or Excel",
        "numeric_missing": "Numeric missing values",
        "categorical_missing": "Categorical missing values",
        "mode": "Mode",
        "unknown_value": "Unknown value",
        "remove_duplicates": "Remove duplicate rows",
        "leave_upload_empty": "Leave the upload empty to use the internal generated dataset bundled with the project.",
        "unable_read_dataset": "Unable to read the dataset: {exc}",
        "uploaded_from_local": "Uploaded from local machine",
        "filters": "## Filters",
        "release_year_range": "Release year range",
        "genres": "Genres",
        "no_rows_match": "No rows match the selected filters. Adjust the year range or genre filter.",
        "hero_eyebrow": "Movie Analysis Studio",
        "hero_title": "Movie analysis dashboard for cleaning, insights, and prediction",
        "hero_desc": "This app covers the core assignment tasks: cleaning missing data, analyzing genres, exploring rating versus revenue, visualizing top movies, and predicting revenue, rating, or view count.",
        "source": "Source",
        "rows": "Rows",
        "movies": "Movies",
        "movies_in_view": "Movies in view",
        "filtered_from_rows": "Filtered from {count} cleaned rows",
        "average_rating": "Average rating",
        "current_top_genre": "Current top genre: {genre}",
        "total_revenue": "Total revenue",
        "average_profit": "Average profit: {value}",
        "average_views": "Average views",
        "based_on_vote_count": "Based on vote count in current view",
        "tab_overview": "Overview",
        "tab_cleaning": "Cleaning",
        "tab_data_quality": "Data Quality",
        "tab_genres": "Genres",
        "tab_compare": "Compare",
        "tab_time_trends": "Time Trends",
        "tab_distribution": "Distribution",
        "tab_rating_revenue": "Rating vs Revenue",
        "tab_top_movies": "Top Movies",
        "tab_movie_detail": "Movie Detail",
        "tab_prediction": "Prediction",
        "tab_data_explorer": "Data Explorer",
        "data_explorer": "Data explorer and export",
        "view_count": "View Count",
        "uploaded_file_prefix": "Uploaded file: {filename}",
        "raw_dataset": "Raw dataset",
        "cleaned_dataset": "Cleaned dataset",
        "download_cleaned_csv": "Download cleaned CSV",
        "download_filtered_csv": "Download filtered CSV",
        "run_prediction": "Run prediction",
        "budget_usd": "Budget (USD)",
        "runtime_minutes": "Runtime (minutes)",
        "release_year": "Release year",
        "current_view_count": "Current view count / vote count",
        "main_genre": "Main genre",
        "studio": "Studio",
        "language_label": "Language",
        "choose_movie": "Choose a movie",
        "peer_movies": "Peer movies",
        "prediction_target": "Prediction target",
        "revenue": "Revenue",
        "rating": "Rating",
        "budget": "Budget",
        "profit": "Profit",
        "roi": "ROI",
        "movie_count": "Movie count",
        "compare_by": "Compare by",
        "genre": "Genre",
        "select_exactly_two": "Select exactly two {label}",
        "choose_exactly_two": "Choose exactly two {label} to unlock the comparison view.",
        "comparison_metric": "Comparison metric",
        "trend_metric": "Trend metric",
        "distribution_metric": "Distribution metric",
        "ranking_metric": "Ranking metric",
        "number_of_movies": "Number of movies",
        "best_model": "Best model",
        "train_rows": "Train: {count} rows",
        "r2_score": "R2 score",
        "closer_to_1": "Closer to 1 means stronger fit",
        "prediction_error": "Prediction error",
        "average_absolute_error": "Average absolute error",
        "predicted_target": "Predicted target",
        "predicted_view_count": "Predicted view count",
        "expected_trend": "Expected trend",
        "most_watched_movie": "Most watched movie",
        "least_watched_movie": "Least watched movie",
        "predicted_movie": "Predicted movie",
        "custom_input_movie": "Custom input movie",
        "type": "Type",
        "title": "Title",
        "views": "Views",
        "scenario_analysis": "Scenario analysis",
        "predicted_value": "Predicted value",
        "predicted_revenue": "Predicted revenue",
        "predicted_rating": "Predicted rating",
        "predicted_view_count_label": "Predicted view count",
        "this_is_streamlit_app": "This is a Streamlit app. Run it with:",
        "or_double_click": "Or double-click run_app.bat / run_app.ps1.",
        "before_cleaning": "Before cleaning",
        "after_cleaning": "After cleaning",
        "missing_values": "Missing values",
        "cleaning_section_title": "Missing-data cleaning",
        "cleaning_section_caption": "This section reports missing values before and after cleaning, duplicate removal, and the fill strategy used by the app.",
        "rows_before_cleaning": "Rows before cleaning",
        "rows_after_cleaning": "Rows after cleaning",
        "original_dataset_size": "Original dataset size",
        "after_optional_duplicate_removal": "After optional duplicate removal",
        "duplicates_removed": "Duplicates removed",
        "based_on_title_year_studio": "Based on title, year, and studio",
        "columns_auto_added": "Columns auto-added",
        "useful_for_custom_datasets": "Useful for custom datasets",
        "cleaning_rules": "Cleaning rules",
        "numeric_fill_values": "Numeric fill values",
        "categorical_fill_values": "Categorical fill values",
        "numeric_columns_use_strategy": "Numeric columns use the <strong>{numeric}</strong> strategy. Categorical columns use <strong>{categorical}</strong> filling.",
        "data_quality_title": "Data quality audit",
        "data_quality_caption": "Profile missing rates, outliers, duplicates, and invalid numeric values before relying on any downstream insight or model output.",
        "raw_rows": "Raw rows",
        "cleaned_rows": "Cleaned rows",
        "raw_duplicates": "Raw duplicates",
        "exact_duplicated_rows": "Exact duplicated rows",
        "worst_missing_column": "Worst missing column",
        "no_invalid_values": "No invalid numeric values were detected in the uploaded raw dataset.",
        "genres_title": "Genre popularity and performance",
        "genres_caption": "Genre frequency answers which categories are most common, while the bubble chart compares average rating and average revenue.",
        "genre_insight": "Genre insight",
        "genre_insight_body": "<strong>{genre}</strong> is the most frequent genre in the current view with <strong>{count}</strong> movie entries after genre expansion.",
        "compare_title": "Compare analysis",
        "compare_caption": "Compare two genres or two studios side by side across movie count, rating, revenue, profit, ROI, and audience reach.",
        "comparison_insight": "Comparison insight",
        "comparison_insight_body": "<strong>{winner}</strong> leads <strong>{metric}</strong> with a gap of <strong>{gap}</strong> over <strong>{runner}</strong>.",
        "time_trends_title": "Time-based trends",
        "time_trends_caption": "Track how movie volume, ratings, revenue, profit, and ROI shift by release year to reveal broader patterns instead of isolated winners.",
        "year_highlights": "Year highlights",
        "year_highlights_body": "The strongest ROI year is <strong>{best_year}</strong> at <strong>{best_roi:.2f}x</strong>. The largest total revenue appears in <strong>{market_year}</strong> with <strong>{market_revenue}</strong>.",
        "distribution_title": "Distribution and correlation",
        "distribution_caption": "Use distributions to see spread and skew, then inspect the full numeric correlation matrix instead of only one pair of variables.",
        "rating_revenue_title": "Relationship between rating and revenue",
        "rating_revenue_caption": "The scatter plot highlights whether higher-rated movies also tend to earn more revenue in the selected data slice.",
        "positive": "positive",
        "negative": "negative",
        "correlation_summary": "Correlation summary",
        "correlation_summary_body": "The Pearson correlation is <strong>{corr:.2f}</strong>, which indicates a <strong>{trend}</strong> relationship between rating and revenue in the filtered data.",
        "revenue_leader": "Revenue leader",
        "revenue_leader_body": "<strong>{title}</strong> currently leads revenue with <strong>{revenue}</strong> and rating <strong>{rating:.1f}</strong>.",
        "top_movies_title": "Top movie visualization",
        "top_movies_caption": "Sort and compare the strongest movies by revenue, rating, budget, profit, or ROI.",
        "main_genre_col": "Main genre",
        "movie_detail_title": "Movie detail drill-down",
        "movie_detail_caption": "Inspect one movie in depth, then benchmark it against the filtered dataset, its genre, its studio, and its release year peers.",
        "selected_rating": "Selected rating",
        "selected_revenue": "Selected revenue",
        "selected_profit": "Selected profit",
        "genre_prefix": "Genre: {genre}",
        "budget_prefix": "Budget: {value}",
        "roi_prefix": "ROI: {value:.2f}x",
        "studio_prefix": "Studio: {studio}",
        "movie_summary": "Movie summary",
        "movie_summary_body": "<strong>{title}</strong> was released in <strong>{year}</strong>. It belongs to <strong>{genre}</strong>, generated <strong>{revenue}</strong> from a budget of <strong>{budget}</strong>, and delivered <strong>{roi:.2f}x</strong> ROI.",
        "benchmarks": "Benchmarks",
        "benchmarks_body": "The movie's rating is <strong>{rating_gap:+.2f}</strong> versus its genre average, and its views are <strong>{views_gap:+,}</strong> versus its studio average.",
        "prediction_title": "Prediction model",
        "prediction_caption": "Train multiple regression models, compare their performance, and run a custom prediction for revenue, rating, or view count.",
        "prediction_context": "The model trains on the current filter, so changing years or genres updates the prediction context.",
        "custom_prediction_title": "Custom prediction",
        "custom_prediction_caption": "Enter a movie profile below to estimate the selected target, expected view trend, and the popularity position against the current dataset.",
        "scenario_caption": "This chart varies the budget while keeping the rest of the movie profile fixed, so you can see how sensitive the prediction is to investment changes.",
        "data_explorer_caption": "Inspect both raw and cleaned datasets, then download the processed data for reporting or further analysis.",
    },
}


def t(lang: str, key: str, **kwargs: object) -> str:
    fallback = TRANSLATIONS["en"].get(key)
    if fallback is None:
        fallback = key.replace("_", " ").title()
    template = TRANSLATIONS.get(lang, {}).get(key, fallback)
    return template.format(**kwargs)

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


def format_target_value(value: float, target_column: str, lang: str = "en") -> str:
    if target_column == "revenue":
        return format_currency(value)
    if target_column == "vote_count":
        unit = "lượt xem" if lang == "vi" else "views"
        return f"{int(round(value)):,} {unit}"
    return f"{value:.2f}/10"


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


def build_data_reference_text(
    lang: str,
    localized_source_label: str,
    sample_path_label: str,
    quality_report: dict[str, object],
    cleaned_df: pd.DataFrame,
) -> tuple[str, str, str]:
    worst_missing_column = str(quality_report["completeness"].iloc[0]["column"])
    if localized_source_label.lower().startswith("uploaded file") or "tải lên" in localized_source_label.lower():
        current_source = (
            f"Dashboard hiện đang dùng <strong>{localized_source_label}</strong>. Vị trí dữ liệu hiện tại: <strong>{sample_path_label}</strong>. "
            "Khi bạn tải file riêng lên, toàn bộ bước làm sạch, phân tích và dự đoán sẽ chạy trên chính file đó."
            if lang == "vi"
            else f"The dashboard is currently using <strong>{localized_source_label}</strong>. Current data location: <strong>{sample_path_label}</strong>. "
            "Once a custom file is uploaded, all cleaning, analysis, and prediction steps run on that file."
        )
    else:
        current_source = (
            f"Dashboard hiện đang dùng <strong>{localized_source_label}</strong> tại <strong>{sample_path_label}</strong>. "
            "Đây là bộ dữ liệu mẫu được sinh sẵn trong project để demo luồng làm sạch, trực quan hóa và dự đoán khi chưa có dữ liệu người dùng tải lên."
            if lang == "vi"
            else f"The dashboard is currently using <strong>{localized_source_label}</strong> at <strong>{sample_path_label}</strong>. "
            "It is a built-in sample dataset generated inside the project to demonstrate cleaning, visualization, and prediction when no user dataset has been uploaded."
        )

    reference_sources = (
        "Nguồn tham chiếu nên dùng cho dữ liệu thật: <strong>TMDb API</strong> cho title, genres, release date, runtime, language, vote_count, vote_average, budget, revenue, studio; "
        "<strong>OMDb API</strong> có thể dùng để bổ sung <strong>Metascore</strong> nếu cần."
        if lang == "vi"
        else "Recommended reference sources for real datasets: <strong>TMDb API</strong> for title, genres, release date, runtime, language, vote_count, vote_average, budget, revenue, and studio; "
        "<strong>OMDb API</strong> can be used to supplement <strong>Metascore</strong> when needed."
    )

    dataset_profile = (
        f"Tập hiện tại có <strong>{len(cleaned_df):,}</strong> dòng sau làm sạch, <strong>{len(cleaned_df.columns)}</strong> cột, "
        f"phạm vi năm phát hành <strong>{int(cleaned_df['release_year'].min())}</strong> đến <strong>{int(cleaned_df['release_year'].max())}</strong>. "
        f"Cột thiếu nhiều nhất trong dữ liệu gốc là <strong>{worst_missing_column}</strong>."
        if lang == "vi"
        else f"The current dataset contains <strong>{len(cleaned_df):,}</strong> cleaned rows, <strong>{len(cleaned_df.columns)}</strong> columns, "
        f"and spans release years from <strong>{int(cleaned_df['release_year'].min())}</strong> to <strong>{int(cleaned_df['release_year'].max())}</strong>. "
        f"The worst missing column in the raw data is <strong>{worst_missing_column}</strong>."
    )
    return current_source, reference_sources, dataset_profile


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
    if metric_column in {"revenue", "budget", "profit"}:
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
    if metric_column in {"revenue", "budget", "profit"}:
        unit_label = "million USD"
    elif metric_column == "roi":
        unit_label = "ROI"
    else:
        unit_label = metric_column.replace("_", " ").title()
    fig.update_layout(xaxis_title=unit_label, yaxis_title="")
    return ranking, style_figure(fig, height=max(380, top_n * 32))


def build_prediction_scatter(prediction_frame: pd.DataFrame, target_column: str, lang: str = "en") -> go.Figure:
    if target_column == "revenue":
        unit = "Doanh thu (USD)" if lang == "vi" else "Revenue (USD)"
    elif target_column == "vote_count":
        unit = "Lượt xem" if lang == "vi" else "View count"
    else:
        unit = "Điểm đánh giá" if lang == "vi" else "Rating"
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
            name="Đường lý tưởng" if lang == "vi" else "Ideal line",
            line=dict(color="#ffd166", width=2.5, dash="dash"),
        )
    )
    actual_label = "Thực tế" if lang == "vi" else "Actual"
    predicted_label = "Dự đoán" if lang == "vi" else "Predicted"
    fig.update_layout(xaxis_title=f"{actual_label} {unit}", yaxis_title=f"{predicted_label} {unit}")
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


def build_data_quality_figure(completeness_frame: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        completeness_frame.sort_values(by="missing_pct", ascending=True),
        x="missing_pct",
        y="column",
        orientation="h",
        color="missing_pct",
        color_continuous_scale=["#123a5a", "#ff8a3d"],
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Missing rate (%)", yaxis_title="")
    return style_figure(fig, height=360)


def build_outlier_figure(outlier_frame: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        outlier_frame.sort_values(by="outlier_count", ascending=True),
        x="outlier_count",
        y="column",
        orientation="h",
        color="outlier_pct",
        color_continuous_scale=["#123a5a", "#12c6c2"],
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Outlier count", yaxis_title="")
    return style_figure(fig, height=360)


def build_time_trend_figure(frame: pd.DataFrame, metric_column: str, metric_label: str) -> go.Figure:
    yearly = (
        frame.groupby("release_year", as_index=False)
        .agg(
            movie_count=("title", "count"),
            avg_rating=("rating", "mean"),
            total_revenue=("revenue", "sum"),
            avg_revenue=("revenue", "mean"),
            avg_profit=("profit", "mean"),
            avg_roi=("roi", "mean"),
        )
        .sort_values(by="release_year")
    )

    fig = px.line(
        yearly,
        x="release_year",
        y=metric_column,
        markers=True,
        color_discrete_sequence=[PALETTE[1]],
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(xaxis_title="Release year", yaxis_title=metric_label)
    return style_figure(fig, height=380)


def build_distribution_figure(frame: pd.DataFrame, column: str, label: str) -> go.Figure:
    fig = px.histogram(
        frame,
        x=column,
        nbins=28,
        color_discrete_sequence=[PALETTE[0]],
        opacity=0.85,
    )
    fig.update_layout(xaxis_title=label, yaxis_title="Movies")
    return style_figure(fig, height=360)


def build_boxplot_figure(frame: pd.DataFrame, column: str, label: str) -> go.Figure:
    fig = px.box(
        frame,
        y=column,
        color_discrete_sequence=[PALETTE[2]],
        points="outliers",
    )
    fig.update_layout(xaxis_title="", yaxis_title=label, showlegend=False)
    return style_figure(fig, height=360)


def build_correlation_heatmap(frame: pd.DataFrame) -> go.Figure:
    corr_columns = ["rating", "revenue", "budget", "runtime", "release_year", "vote_count", "metascore", "profit", "roi"]
    corr_frame = frame[corr_columns].corr(numeric_only=True).round(2)
    fig = px.imshow(
        corr_frame,
        text_auto=True,
        color_continuous_scale=["#07111f", "#12c6c2", "#ffd166", "#ff8a3d"],
        aspect="auto",
    )
    fig.update_layout(coloraxis_colorbar_title="Corr")
    return style_figure(fig, height=500)


def build_roi_top_figure(frame: pd.DataFrame, top_n: int = 10) -> go.Figure:
    ranking = frame.sort_values(by="roi", ascending=False).head(top_n).sort_values(by="roi", ascending=True)
    fig = px.bar(
        ranking,
        x="roi",
        y="title",
        orientation="h",
        color="primary_genre",
        color_discrete_sequence=PALETTE,
        hover_data={"profit": ":,.0f", "revenue": ":,.0f", "budget": ":,.0f"},
    )
    fig.update_layout(xaxis_title="ROI (Revenue / Budget)", yaxis_title="")
    return style_figure(fig, height=max(360, top_n * 32))


def summarize_comparison_group(frame: pd.DataFrame, dimension: str, selected_values: list[str]) -> pd.DataFrame:
    if dimension == "genre":
        expanded = explode_genres(frame)
        comparison = expanded[expanded["genre_item"].isin(selected_values)].copy()
        grouped = (
            comparison.groupby("genre_item", as_index=False)
            .agg(
                movie_count=("title", "count"),
                avg_rating=("rating", "mean"),
                avg_revenue=("revenue", "mean"),
                avg_profit=("profit", "mean"),
                avg_roi=("roi", "mean"),
                avg_views=("vote_count", "mean"),
            )
            .rename(columns={"genre_item": "group"})
        )
    else:
        comparison = frame[frame["studio"].isin(selected_values)].copy()
        grouped = (
            comparison.groupby("studio", as_index=False)
            .agg(
                movie_count=("title", "count"),
                avg_rating=("rating", "mean"),
                avg_revenue=("revenue", "mean"),
                avg_profit=("profit", "mean"),
                avg_roi=("roi", "mean"),
                avg_views=("vote_count", "mean"),
            )
            .rename(columns={"studio": "group"})
        )

    return grouped.sort_values(by="group").reset_index(drop=True)


def build_comparison_figure(comparison_frame: pd.DataFrame, metric_column: str, metric_label: str) -> go.Figure:
    fig = px.bar(
        comparison_frame,
        x="group",
        y=metric_column,
        color="group",
        color_discrete_sequence=PALETTE,
        text_auto=".2s" if metric_column not in {"avg_rating", "avg_roi"} else ".2f",
    )
    fig.update_layout(xaxis_title="", yaxis_title=metric_label, showlegend=False)
    return style_figure(fig, height=380)


def build_movie_percentile(value: float, series: pd.Series) -> float:
    ranked = series.dropna()
    if ranked.empty:
        return 0.0
    return float((ranked <= value).mean() * 100)


def build_movie_profile(selected_movie: pd.Series, frame: pd.DataFrame) -> pd.DataFrame:
    genre_slice = frame[frame["primary_genre"] == selected_movie["primary_genre"]]
    studio_slice = frame[frame["studio"] == selected_movie["studio"]]
    year_slice = frame[frame["release_year"] == selected_movie["release_year"]]

    profile_rows = [
        {
            "metric": "Rating percentile",
            "value": f"{build_movie_percentile(float(selected_movie['rating']), frame['rating']):.1f}%",
            "benchmark": "Against current filtered dataset",
        },
        {
            "metric": "Revenue percentile",
            "value": f"{build_movie_percentile(float(selected_movie['revenue']), frame['revenue']):.1f}%",
            "benchmark": "Against current filtered dataset",
        },
        {
            "metric": "Profit percentile",
            "value": f"{build_movie_percentile(float(selected_movie['profit']), frame['profit']):.1f}%",
            "benchmark": "Against current filtered dataset",
        },
        {
            "metric": "Genre average rating gap",
            "value": f"{float(selected_movie['rating']) - float(genre_slice['rating'].mean()):+.2f}",
            "benchmark": f"Vs {selected_movie['primary_genre']} average",
        },
        {
            "metric": "Studio average revenue gap",
            "value": format_currency(float(selected_movie["revenue"]) - float(studio_slice["revenue"].mean())),
            "benchmark": f"Vs {selected_movie['studio']} average",
        },
        {
            "metric": "Year average ROI gap",
            "value": f"{float(selected_movie['roi']) - float(year_slice['roi'].mean()):+.2f}x",
            "benchmark": f"Vs {int(selected_movie['release_year'])} average",
        },
    ]
    return pd.DataFrame(profile_rows)


def build_movie_peer_table(selected_movie: pd.Series, frame: pd.DataFrame) -> pd.DataFrame:
    peers = frame[
        (frame["primary_genre"] == selected_movie["primary_genre"])
        & (frame["release_year"].between(int(selected_movie["release_year"]) - 1, int(selected_movie["release_year"]) + 1))
    ].copy()
    peers["distance"] = (
        (peers["rating"] - float(selected_movie["rating"])).abs()
        + ((peers["roi"] - float(selected_movie["roi"])).abs() * 0.6)
    )
    peers = peers.sort_values(by="distance", ascending=True)
    peers = peers[peers["title"] != selected_movie["title"]].head(5)
    return peers[["title", "primary_genre", "studio", "release_year", "rating", "revenue", "profit", "roi"]]


def build_scenario_figure(model_bundle: dict[str, object], payload: dict[str, object], target_column: str) -> pd.DataFrame:
    baseline_budget = float(payload["budget"])
    scenario_rows: list[dict[str, float]] = []
    for multiplier in [0.7, 0.85, 1.0, 1.15, 1.3]:
        scenario_payload = dict(payload)
        scenario_payload["budget"] = max(1_000_000.0, baseline_budget * multiplier)
        predicted_value = predict_single(model_bundle, scenario_payload, target_column=target_column)
        scenario_rows.append(
            {
                "budget": scenario_payload["budget"],
                "predicted": predicted_value,
                "scenario": f"{multiplier:.0%} budget",
            }
        )
    return pd.DataFrame(scenario_rows)


def classify_view_level(predicted_views: float, frame: pd.DataFrame) -> str:
    low_threshold = float(frame["vote_count"].quantile(0.25))
    high_threshold = float(frame["vote_count"].quantile(0.75))
    if predicted_views >= high_threshold:
        return "high"
    if predicted_views <= low_threshold:
        return "low"
    return "medium"


def compare_view_trend(predicted_views: float, baseline_views: float | None, frame: pd.DataFrame) -> str:
    if baseline_views is not None and baseline_views > 0:
        if predicted_views > baseline_views:
            return "increase"
        if predicted_views < baseline_views:
            return "decrease"
        return "stay stable"

    median_views = float(frame["vote_count"].median())
    if predicted_views > median_views:
        return "increase"
    if predicted_views < median_views:
        return "decrease"
    return "stay stable"


def build_prediction_summary(
    target_column: str,
    predicted_target: float,
    predicted_views: float,
    baseline_views: float | None,
    frame: pd.DataFrame,
    lang: str = "en",
) -> tuple[str, str, str]:
    level = classify_view_level(predicted_views, frame)
    trend = compare_view_trend(predicted_views, baseline_views, frame)
    level_map = {
        "vi": {"high": "cao", "medium": "trung bình", "low": "thấp"},
        "en": {"high": "high", "medium": "medium", "low": "low"},
    }
    trend_map = {
        "vi": {"increase": "tăng", "decrease": "giảm", "stay stable": "giữ ổn định"},
        "en": {"increase": "increase", "decrease": "decrease", "stay stable": "stay stable"},
    }
    level_text = level_map[lang][level]
    trend_text_value = trend_map[lang][trend]

    if target_column == "revenue":
        lead_text = (
            f"Doanh thu dự đoán là {format_target_value(predicted_target, target_column, lang)}."
            if lang == "vi"
            else f"Predicted revenue is {format_target_value(predicted_target, target_column, lang)}."
        )
    elif target_column == "rating":
        lead_text = (
            f"Rating dự đoán là {format_target_value(predicted_target, target_column, lang)}."
            if lang == "vi"
            else f"Predicted rating is {format_target_value(predicted_target, target_column, lang)}."
        )
    else:
        lead_text = (
            f"Lượt xem dự đoán là {format_target_value(predicted_target, target_column, lang)}."
            if lang == "vi"
            else f"Predicted view count is {format_target_value(predicted_target, target_column, lang)}."
        )

    trend_text = (
        (
            f"Bộ phim được dự đoán sẽ {trend_text_value} về độ phổ biến, với khoảng {int(round(predicted_views)):,} lượt xem "
            f"và mức độ quan tâm {level_text} so với tập dữ liệu hiện tại."
        )
        if lang == "vi"
        else (
            f"The movie is expected to {trend_text_value} in popularity, with an estimated {int(round(predicted_views)):,} views "
            f"and a {level_text} viewing level compared with the current dataset."
        )
    )

    most_watched = frame.sort_values(by="vote_count", ascending=False).iloc[0]
    least_watched = frame.sort_values(by="vote_count", ascending=True).iloc[0]
    benchmark_text = (
        (
            f"Phim đang có lượt xem cao nhất là {most_watched['title']} với {most_watched['vote_count']:,} lượt xem, "
            f"trong khi phim thấp nhất là {least_watched['title']} với {least_watched['vote_count']:,} lượt xem."
        )
        if lang == "vi"
        else (
            f"Most watched movie right now is {most_watched['title']} with {most_watched['vote_count']:,} views, "
            f"while the least watched is {least_watched['title']} with {least_watched['vote_count']:,} views."
        )
    )
    return lead_text, trend_text, benchmark_text


def main() -> None:
    lang_label = st.session_state.get("language_label", "Tiếng Việt")
    lang = LANGUAGE_OPTIONS.get(lang_label, "vi")
    st.set_page_config(
        page_title=t(lang, "app_title"),
        page_icon="MC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)
    language_label = st.sidebar.selectbox("Language / Ngôn ngữ", options=list(LANGUAGE_OPTIONS.keys()), index=0)
    st.session_state["language_label"] = language_label
    lang = LANGUAGE_OPTIONS[language_label]
    st.sidebar.markdown(t(lang, "sidebar_control"))
    uploaded_file = st.sidebar.file_uploader(t(lang, "upload"), type=["csv", "xlsx", "xls"])
    numeric_strategy = st.sidebar.selectbox(
        t(lang, "numeric_missing"),
        options=["median", "mean"],
        format_func=lambda value: value.title(),
    )
    categorical_strategy = st.sidebar.selectbox(
        t(lang, "categorical_missing"),
        options=["mode", "constant"],
        format_func=lambda value: t(lang, "mode") if value == "mode" else t(lang, "unknown_value"),
    )
    drop_duplicates = st.sidebar.toggle(t(lang, "remove_duplicates"), value=True)
    st.sidebar.caption(t(lang, "leave_upload_empty"))

    try:
        if uploaded_file is None:
            raw_df, source_label, dataset_path = load_sample_dataset(BASE_DIR)
            sample_path_label = str(dataset_path.relative_to(BASE_DIR))
        else:
            raw_df, source_label = load_uploaded_dataset(uploaded_file.getvalue(), uploaded_file.name)
            sample_path_label = t(lang, "uploaded_from_local")
    except Exception as exc:
        st.error(t(lang, "unable_read_dataset", exc=exc))
        return

    cleaned_df, cleaning_report = clean_movie_data(
        raw_df,
        numeric_strategy=numeric_strategy,
        categorical_strategy=categorical_strategy,
        drop_duplicates=drop_duplicates,
    )
    quality_report = build_data_quality_report(raw_df, cleaned_df)

    available_genres = sorted(explode_genres(cleaned_df)["genre_item"].dropna().unique().tolist())
    year_min = int(cleaned_df["release_year"].min())
    year_max = int(cleaned_df["release_year"].max())

    st.sidebar.markdown("---")
    st.sidebar.markdown(t(lang, "filters"))
    selected_years = st.sidebar.slider(t(lang, "release_year_range"), min_value=year_min, max_value=year_max, value=(year_min, year_max))
    selected_genres = st.sidebar.multiselect(t(lang, "genres"), options=available_genres)

    filtered_df = cleaned_df[cleaned_df["release_year"].between(selected_years[0], selected_years[1])].copy()
    filtered_df = filter_by_genres(filtered_df, selected_genres).reset_index(drop=True)

    if filtered_df.empty:
        st.warning(t(lang, "no_rows_match"))
        return

    genre_frame = explode_genres(filtered_df)
    genre_counts = genre_frame["genre_item"].value_counts()
    top_genre = genre_counts.index[0] if not genre_counts.empty else "Unknown"
    avg_rating = filtered_df["rating"].mean()
    total_revenue = filtered_df["revenue"].sum()
    average_budget = filtered_df["budget"].mean()
    average_views = filtered_df["vote_count"].mean()
    average_profit = filtered_df["profit"].mean()
    average_roi = filtered_df["roi"].mean()
    correlation = filtered_df["rating"].corr(filtered_df["revenue"])
    if pd.isna(correlation):
        correlation = 0.0

    localized_source_label = source_label
    if source_label == "Internal generated movie dataset":
        localized_source_label = "Bộ dữ liệu nội bộ do project tạo" if lang == "vi" else source_label
    elif source_label.startswith("Uploaded file:"):
        uploaded_name = source_label.split(":", 1)[1].strip()
        localized_source_label = t(lang, "uploaded_file_prefix", filename=uploaded_name)
    current_source_text, reference_sources_text, dataset_profile_text = build_data_reference_text(
        lang=lang,
        localized_source_label=localized_source_label,
        sample_path_label=sample_path_label,
        quality_report=quality_report,
        cleaned_df=cleaned_df,
    )

    st.markdown(
        hero_card(
            t(lang, "hero_eyebrow"),
            t(lang, "hero_title"),
            t(lang, "hero_desc"),
            t(lang, "source"),
            t(lang, "rows"),
            t(lang, "genres"),
            localized_source_label,
            len(filtered_df),
            len(genre_counts.index),
        ),
        unsafe_allow_html=True,
    )

    render_metric_row(
        [
            (t(lang, "movies_in_view"), format_compact_number(len(filtered_df)), t(lang, "filtered_from_rows", count=len(cleaned_df))),
            (t(lang, "average_rating"), f"{avg_rating:.2f}/10", t(lang, "current_top_genre", genre=top_genre)),
            (t(lang, "total_revenue"), format_currency(total_revenue), t(lang, "average_profit", value=format_currency(average_profit))),
            (t(lang, "average_views"), f"{int(round(average_views)):,}", t(lang, "based_on_vote_count")),
        ]
    )

    st.markdown("")
    tabs = st.tabs(
        [
            t(lang, "tab_overview"),
            t(lang, "tab_cleaning"),
            t(lang, "tab_data_quality"),
            t(lang, "tab_genres"),
            t(lang, "tab_compare"),
            t(lang, "tab_time_trends"),
            t(lang, "tab_distribution"),
            t(lang, "tab_rating_revenue"),
            t(lang, "tab_top_movies"),
            t(lang, "tab_movie_detail"),
            t(lang, "tab_prediction"),
            t(lang, "tab_data_explorer"),
        ]
    )

    with tabs[0]:
        st.markdown(
            section_header(
                "Tổng quan dự án" if lang == "vi" else "Project overview",
                "Góc nhìn tổng quát về bộ dữ liệu hiện tại, các insight chính và những yêu cầu đề tài mà ứng dụng đang đáp ứng."
                if lang == "vi"
                else "A focused view of the current dataset, key findings, and the exact assignment requirements covered by the app.",
            ),
            unsafe_allow_html=True,
        )
        left_col, right_col = st.columns([1.35, 1])
        with left_col:
            st.dataframe(
                filtered_df.head(12),
                width="stretch",
                column_config={
                    "revenue": st.column_config.NumberColumn(t(lang, "revenue"), format="$ %.0f"),
                    "budget": st.column_config.NumberColumn(t(lang, "budget"), format="$ %.0f"),
                    "rating": st.column_config.NumberColumn(t(lang, "rating"), format="%.1f"),
                },
            )
        with right_col:
            st.markdown(
                insight_card(
                    "Nguồn dữ liệu hiện tại" if lang == "vi" else "Current dataset",
                    current_source_text,
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Nguồn tham chiếu đề xuất" if lang == "vi" else "Recommended references",
                    reference_sources_text,
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Tổng quan dữ liệu" if lang == "vi" else "Dataset profile",
                    dataset_profile_text,
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Insight chính" if lang == "vi" else "Core insight",
                    (
                        f"<strong>{top_genre}</strong> xuất hiện nhiều nhất trong tập dữ liệu đã lọc, với rating trung bình <strong>{avg_rating:.2f}</strong>, tổng doanh thu <strong>{format_currency(total_revenue)}</strong> và ROI trung bình <strong>{average_roi:.2f}x</strong>."
                        if lang == "vi"
                        else f"<strong>{top_genre}</strong> appears most often in the filtered data, with an average rating of <strong>{avg_rating:.2f}</strong>, total revenue of <strong>{format_currency(total_revenue)}</strong>, and average ROI of <strong>{average_roi:.2f}x</strong>."
                    ),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Checklist đề tài" if lang == "vi" else "Assignment checklist",
                    "Ứng dụng tự động làm sạch dữ liệu thiếu, theo dõi tần suất thể loại, so sánh trực quan rating và doanh thu, xếp hạng top phim và huấn luyện mô hình hồi quy để dự đoán."
                    if lang == "vi"
                    else "Missing values are cleaned automatically, genre frequency is tracked, rating and revenue are compared visually, top movies are ranked, and regression models are trained for prediction.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    "Điểm nhanh về độ phổ biến" if lang == "vi" else "Popularity snapshot",
                    (
                        f"Phim có lượt xem cao nhất hiện tại là <strong>{filtered_df.sort_values(by='vote_count', ascending=False).iloc[0]['title']}</strong>, "
                        f"trong khi phim thấp nhất là <strong>{filtered_df.sort_values(by='vote_count', ascending=True).iloc[0]['title']}</strong>."
                        if lang == "vi"
                        else f"The current most watched movie is <strong>{filtered_df.sort_values(by='vote_count', ascending=False).iloc[0]['title']}</strong>, "
                        f"while the least watched movie is <strong>{filtered_df.sort_values(by='vote_count', ascending=True).iloc[0]['title']}</strong>."
                    ),
                ),
                unsafe_allow_html=True,
            )

    with tabs[1]:
        st.markdown(
            section_header(
                t(lang, "cleaning_section_title"),
                t(lang, "cleaning_section_caption"),
            ),
            unsafe_allow_html=True,
        )
        render_metric_row(
            [
                (t(lang, "rows_before_cleaning"), format_compact_number(cleaning_report["rows_before"]), t(lang, "original_dataset_size")),
                (t(lang, "rows_after_cleaning"), format_compact_number(cleaning_report["rows_after"]), t(lang, "after_optional_duplicate_removal")),
                (t(lang, "duplicates_removed"), format_compact_number(cleaning_report["duplicates_removed"]), t(lang, "based_on_title_year_studio")),
                (t(lang, "columns_auto_added"), format_compact_number(len(cleaning_report["added_columns"])), t(lang, "useful_for_custom_datasets")),
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
                    t(lang, "cleaning_rules"),
                    t(
                        lang,
                        "numeric_columns_use_strategy",
                        numeric=cleaning_report["numeric_strategy"],
                        categorical=cleaning_report["categorical_strategy"],
                    ),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    t(lang, "numeric_fill_values"),
                    numeric_fill_summary,
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    t(lang, "categorical_fill_values"),
                    categorical_fill_summary,
                ),
                unsafe_allow_html=True,
            )

        missing_table = pd.DataFrame(
            {
                "Column": list(cleaning_report["missing_before"].keys()),
                t(lang, "before_cleaning"): list(cleaning_report["missing_before"].values()),
                t(lang, "after_cleaning"): [cleaning_report["missing_after"].get(key, 0) for key in cleaning_report["missing_before"].keys()],
            }
        )
        st.dataframe(missing_table, width="stretch")

    with tabs[2]:
        st.markdown(
            section_header(
                t(lang, "data_quality_title"),
                t(lang, "data_quality_caption"),
            ),
            unsafe_allow_html=True,
        )
        quality_col1, quality_col2 = st.columns(2)
        with quality_col1:
            render_metric_row(
                [
                    (t(lang, "raw_rows"), format_compact_number(quality_report["raw_row_count"]), t(lang, "before_cleaning")),
                    (t(lang, "cleaned_rows"), format_compact_number(quality_report["cleaned_row_count"]), t(lang, "after_cleaning")),
                    (t(lang, "raw_duplicates"), format_compact_number(quality_report["duplicate_rows_raw"]), t(lang, "exact_duplicated_rows")),
                    (
                        t(lang, "worst_missing_column"),
                        quality_report["completeness"].iloc[0]["column"],
                        f"{quality_report['completeness'].iloc[0]['missing_pct']:.1f}% missing" if lang == "en" else f"{quality_report['completeness'].iloc[0]['missing_pct']:.1f}% thiếu",
                    ),
                ]
            )
            st.plotly_chart(build_data_quality_figure(quality_report["completeness"]), width="stretch")
        with quality_col2:
            st.plotly_chart(build_outlier_figure(quality_report["outliers"]), width="stretch")
            if not quality_report["invalids"].empty:
                st.dataframe(quality_report["invalids"], width="stretch")
            else:
                st.info(t(lang, "no_invalid_values"))

        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.dataframe(quality_report["completeness"], width="stretch")
        with detail_col2:
            st.dataframe(quality_report["outliers"], width="stretch")

    with tabs[3]:
        st.markdown(
            section_header(
                t(lang, "genres_title"),
                t(lang, "genres_caption"),
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
                t(lang, "genre_insight"),
                t(lang, "genre_insight_body", genre=top_genre, count=dominant_genre_count),
            ),
                unsafe_allow_html=True,
            )

    with tabs[4]:
        st.markdown(
            section_header(
                t(lang, "compare_title"),
                t(lang, "compare_caption"),
            ),
            unsafe_allow_html=True,
        )
        compare_dimension = st.radio(
            t(lang, "compare_by"),
            options=[t(lang, "genre"), t(lang, "studio")],
            horizontal=True,
            key="compare_dimension",
        )
        if compare_dimension == t(lang, "genre"):
            compare_options = available_genres
            compare_key = "compare_genres"
        else:
            compare_options = sorted(filtered_df["studio"].dropna().astype(str).unique().tolist())
            compare_key = "compare_studios"

        default_selection = compare_options[:2] if len(compare_options) >= 2 else compare_options
        selected_groups = st.multiselect(
            t(lang, "select_exactly_two", label=compare_dimension.lower()),
            options=compare_options,
            default=default_selection,
            max_selections=2,
            key=compare_key,
        )

        if len(selected_groups) != 2:
            st.info(t(lang, "choose_exactly_two", label=compare_dimension.lower()))
        else:
            comparison_frame = summarize_comparison_group(
                filtered_df,
                dimension="genre" if compare_dimension == t(lang, "genre") else "studio",
                selected_values=selected_groups,
            )
            metric_choice = st.selectbox(
                t(lang, "comparison_metric"),
                options=[t(lang, "movie_count"), t(lang, "average_rating"), t(lang, "revenue"), t(lang, "profit"), t(lang, "roi"), t(lang, "average_views")],
                key="compare_metric",
            )
            comparison_metric_map = {
                t(lang, "movie_count"): ("movie_count", t(lang, "movies")),
                t(lang, "average_rating"): ("avg_rating", t(lang, "average_rating")),
                t(lang, "revenue"): ("avg_revenue", f"{t(lang, 'revenue')} (USD)"),
                t(lang, "profit"): ("avg_profit", f"{t(lang, 'profit')} (USD)"),
                t(lang, "roi"): ("avg_roi", t(lang, "roi")),
                t(lang, "average_views"): ("avg_views", t(lang, "average_views")),
            }
            comparison_fig = build_comparison_figure(comparison_frame, *comparison_metric_map[metric_choice])
            compare_col1, compare_col2 = st.columns([1.2, 1])
            with compare_col1:
                st.plotly_chart(comparison_fig, width="stretch")
            with compare_col2:
                st.dataframe(comparison_frame, width="stretch")

                winner_row = comparison_frame.sort_values(by=comparison_metric_map[metric_choice][0], ascending=False).iloc[0]
                runner_row = comparison_frame.sort_values(by=comparison_metric_map[metric_choice][0], ascending=False).iloc[1]
                gap = float(winner_row[comparison_metric_map[metric_choice][0]] - runner_row[comparison_metric_map[metric_choice][0]])
                gap_text = f"{gap:.2f}" if metric_choice in {t(lang, "average_rating"), t(lang, "roi")} else format_compact_number(gap)
                st.markdown(
                    insight_card(
                        t(lang, "comparison_insight"),
                        t(lang, "comparison_insight_body", winner=winner_row["group"], metric=metric_choice.lower(), gap=gap_text, runner=runner_row["group"]),
                    ),
                    unsafe_allow_html=True,
                )

    with tabs[5]:
        st.markdown(
            section_header(
                t(lang, "time_trends_title"),
                t(lang, "time_trends_caption"),
            ),
            unsafe_allow_html=True,
        )
        trend_option = st.selectbox(
            t(lang, "trend_metric"),
            options=[
                t(lang, "movie_count"),
                t(lang, "average_rating"),
                t(lang, "total_revenue"),
                t(lang, "revenue"),
                t(lang, "profit"),
                t(lang, "roi"),
            ],
            key="trend_metric",
        )
        trend_map = {
            t(lang, "movie_count"): ("movie_count", t(lang, "movies")),
            t(lang, "average_rating"): ("avg_rating", t(lang, "average_rating")),
            t(lang, "total_revenue"): ("total_revenue", f"{t(lang, 'total_revenue')} (USD)"),
            t(lang, "revenue"): ("avg_revenue", f"{t(lang, 'revenue')} (USD)"),
            t(lang, "profit"): ("avg_profit", f"{t(lang, 'profit')} (USD)"),
            t(lang, "roi"): ("avg_roi", t(lang, "roi")),
        }
        trend_fig = build_time_trend_figure(filtered_df, *trend_map[trend_option])
        trend_col1, trend_col2 = st.columns([1.45, 1])
        with trend_col1:
            st.plotly_chart(trend_fig, width="stretch")
        with trend_col2:
            yearly_summary = (
                filtered_df.groupby("release_year", as_index=False)
                .agg(
                    movie_count=("title", "count"),
                    avg_rating=("rating", "mean"),
                    total_revenue=("revenue", "sum"),
                    avg_profit=("profit", "mean"),
                    avg_roi=("roi", "mean"),
                )
                .sort_values(by="release_year", ascending=False)
            )
            best_roi_year = yearly_summary.sort_values(by="avg_roi", ascending=False).iloc[0]
            biggest_market_year = yearly_summary.sort_values(by="total_revenue", ascending=False).iloc[0]
            st.markdown(
                insight_card(
                    t(lang, "year_highlights"),
                    t(
                        lang,
                        "year_highlights_body",
                        best_year=int(best_roi_year["release_year"]),
                        best_roi=float(best_roi_year["avg_roi"]),
                        market_year=int(biggest_market_year["release_year"]),
                        market_revenue=format_currency(biggest_market_year["total_revenue"]),
                    ),
                ),
                unsafe_allow_html=True,
            )
            st.dataframe(yearly_summary.head(10), width="stretch")

    with tabs[6]:
        st.markdown(
            section_header(
                t(lang, "distribution_title"),
                t(lang, "distribution_caption"),
            ),
            unsafe_allow_html=True,
        )
        distribution_choice = st.selectbox(
            t(lang, "distribution_metric"),
            options=[t(lang, "rating"), t(lang, "revenue"), t(lang, "budget"), t(lang, "runtime_minutes"), t(lang, "view_count"), t(lang, "profit"), t(lang, "roi")],
            key="distribution_metric",
        )
        distribution_map = {
            t(lang, "rating"): ("rating", t(lang, "rating")),
            t(lang, "revenue"): ("revenue", f"{t(lang, 'revenue')} (USD)"),
            t(lang, "budget"): ("budget", f"{t(lang, 'budget')} (USD)"),
            t(lang, "runtime_minutes"): ("runtime", t(lang, "runtime_minutes")),
            t(lang, "view_count"): ("vote_count", t(lang, "view_count")),
            t(lang, "profit"): ("profit", f"{t(lang, 'profit')} (USD)"),
            t(lang, "roi"): ("roi", t(lang, "roi")),
        }
        dist_column, dist_label = distribution_map[distribution_choice]
        dist_col1, dist_col2 = st.columns(2)
        with dist_col1:
            st.plotly_chart(build_distribution_figure(filtered_df, dist_column, dist_label), width="stretch")
        with dist_col2:
            st.plotly_chart(build_boxplot_figure(filtered_df, dist_column, dist_label), width="stretch")

        st.plotly_chart(build_correlation_heatmap(filtered_df), width="stretch")

    with tabs[7]:
        st.markdown(
            section_header(
                t(lang, "rating_revenue_title"),
                t(lang, "rating_revenue_caption"),
            ),
            unsafe_allow_html=True,
        )
        scatter_fig, scatter_correlation = build_rating_revenue_figure(filtered_df)
        scatter_col, summary_col = st.columns([1.5, 1])
        with scatter_col:
            st.plotly_chart(scatter_fig, width="stretch")
        with summary_col:
            trend_message = t(lang, "positive") if scatter_correlation >= 0 else t(lang, "negative")
            strongest_movie = filtered_df.sort_values(by="revenue", ascending=False).iloc[0]
            st.markdown(
                insight_card(
                    t(lang, "correlation_summary"),
                    t(lang, "correlation_summary_body", corr=scatter_correlation, trend=trend_message),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                insight_card(
                    t(lang, "revenue_leader"),
                    t(
                        lang,
                        "revenue_leader_body",
                        title=strongest_movie["title"],
                        revenue=format_currency(strongest_movie["revenue"]),
                        rating=float(strongest_movie["rating"]),
                    ),
                ),
                unsafe_allow_html=True,
            )

    with tabs[8]:
        st.markdown(
            section_header(
                t(lang, "top_movies_title"),
                t(lang, "top_movies_caption"),
            ),
            unsafe_allow_html=True,
        )
        control_col1, control_col2 = st.columns([1, 1])
        with control_col1:
            ranking_metric_label = st.selectbox(t(lang, "ranking_metric"), options=[t(lang, "revenue"), t(lang, "rating"), t(lang, "budget"), t(lang, "profit"), t(lang, "roi")], key="ranking_metric")
        with control_col2:
            top_n = st.slider(t(lang, "number_of_movies"), min_value=5, max_value=20, value=10)

        metric_map = {t(lang, "revenue"): "revenue", t(lang, "rating"): "rating", t(lang, "budget"): "budget", t(lang, "profit"): "profit", t(lang, "roi"): "roi"}
        ranking_frame, ranking_fig = build_top_movies_figure(filtered_df, metric_map[ranking_metric_label], top_n)
        chart_col, table_col = st.columns([1.15, 1])
        with chart_col:
            st.plotly_chart(ranking_fig, width="stretch")
        with table_col:
            st.dataframe(
                ranking_frame[["title", "primary_genre", "rating", "revenue", "budget", "profit", "roi", "release_year"]],
                width="stretch",
                column_config={
                    "title": t(lang, "title"),
                    "primary_genre": t(lang, "main_genre_col"),
                    "rating": st.column_config.NumberColumn(t(lang, "rating"), format="%.1f"),
                    "revenue": st.column_config.NumberColumn(t(lang, "revenue"), format="$ %.0f"),
                    "budget": st.column_config.NumberColumn(t(lang, "budget"), format="$ %.0f"),
                    "profit": st.column_config.NumberColumn(t(lang, "profit"), format="$ %.0f"),
                    "roi": st.column_config.NumberColumn(t(lang, "roi"), format="%.2f"),
                },
            )

        st.plotly_chart(build_roi_top_figure(filtered_df, top_n=min(top_n, 10)), width="stretch")

    with tabs[9]:
        st.markdown(
            section_header(
                t(lang, "movie_detail_title"),
                t(lang, "movie_detail_caption"),
            ),
            unsafe_allow_html=True,
        )
        movie_options = filtered_df.sort_values(by=["release_year", "title"], ascending=[False, True])["title"].tolist()
        selected_title = st.selectbox(t(lang, "choose_movie"), options=movie_options, key="movie_detail_title")
        movie_row = filtered_df.loc[filtered_df["title"] == selected_title].iloc[0]

        render_metric_row(
            [
                (t(lang, "selected_rating"), f"{float(movie_row['rating']):.1f}/10", t(lang, "genre_prefix", genre=movie_row["primary_genre"])),
                (t(lang, "selected_revenue"), format_currency(float(movie_row["revenue"])), t(lang, "budget_prefix", value=format_currency(float(movie_row["budget"])))),
                (t(lang, "selected_profit"), format_currency(float(movie_row["profit"])), t(lang, "roi_prefix", value=float(movie_row["roi"]))),
                (t(lang, "views"), f"{int(movie_row['vote_count']):,}", t(lang, "studio_prefix", studio=movie_row["studio"])),
            ]
        )

        detail_col1, detail_col2 = st.columns([1.15, 1])
        with detail_col1:
            movie_profile = build_movie_profile(movie_row, filtered_df)
            st.dataframe(movie_profile, width="stretch")
        with detail_col2:
            st.markdown(
                insight_card(
                    t(lang, "movie_summary"),
                    t(
                        lang,
                        "movie_summary_body",
                        title=movie_row["title"],
                        year=int(movie_row["release_year"]),
                        genre=movie_row["primary_genre"],
                        revenue=format_currency(float(movie_row["revenue"])),
                        budget=format_currency(float(movie_row["budget"])),
                        roi=float(movie_row["roi"]),
                    ),
                ),
                unsafe_allow_html=True,
            )

            genre_average_rating = float(filtered_df.loc[filtered_df["primary_genre"] == movie_row["primary_genre"], "rating"].mean())
            studio_average_views = float(filtered_df.loc[filtered_df["studio"] == movie_row["studio"], "vote_count"].mean())
            st.markdown(
                insight_card(
                    t(lang, "benchmarks"),
                    t(
                        lang,
                        "benchmarks_body",
                        rating_gap=float(movie_row["rating"]) - genre_average_rating,
                        views_gap=int(round(float(movie_row["vote_count"]) - studio_average_views)),
                    ),
                ),
                unsafe_allow_html=True,
            )

        st.markdown(f"### {t(lang, 'peer_movies')}")
        st.dataframe(
            build_movie_peer_table(movie_row, filtered_df),
            width="stretch",
            column_config={
                "rating": st.column_config.NumberColumn(t(lang, "rating"), format="%.1f"),
                "revenue": st.column_config.NumberColumn(t(lang, "revenue"), format="$ %.0f"),
                "profit": st.column_config.NumberColumn(t(lang, "profit"), format="$ %.0f"),
                "roi": st.column_config.NumberColumn(t(lang, "roi"), format="%.2f"),
            },
        )

    with tabs[10]:
        st.markdown(
            section_header(
                t(lang, "prediction_title"),
                t(lang, "prediction_caption"),
            ),
            unsafe_allow_html=True,
        )
        target_label = st.selectbox(t(lang, "prediction_target"), options=[t(lang, "revenue"), t(lang, "rating"), t(lang, "view_count")], key="prediction_target")
        target_column = {t(lang, "revenue"): "revenue", t(lang, "rating"): "rating", t(lang, "view_count"): "vote_count"}[target_label]
        st.caption(t(lang, "prediction_context"))

        try:
            model_bundle = train_regression_models(filtered_df, target_column=target_column)
            popularity_bundle = model_bundle if target_column == "vote_count" else train_regression_models(filtered_df, target_column="vote_count")
        except ValueError as exc:
            st.warning(str(exc))
        else:
            best_model_row = model_bundle["best_model_metrics"]
            render_metric_row(
                [
                    (t(lang, "best_model"), model_bundle["best_model_name"], t(lang, "train_rows", count=model_bundle["train_size"])),
                    (t(lang, "r2_score"), f"{best_model_row['R2']:.3f}", t(lang, "closer_to_1")),
                    ("RMSE", format_target_value(best_model_row["RMSE"], target_column, lang), t(lang, "prediction_error")),
                    ("MAE", format_target_value(best_model_row["MAE"], target_column, lang), t(lang, "average_absolute_error")),
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
                    "CV_R2": st.column_config.NumberColumn("CV R2", format="%.3f"),
                    "CV_RMSE": st.column_config.NumberColumn("CV RMSE", format="%.3f"),
                },
            )

            importance_col, prediction_col = st.columns(2)
            with importance_col:
                st.plotly_chart(build_feature_importance_figure(model_bundle["feature_importance"]), width="stretch")
            with prediction_col:
                st.plotly_chart(
                    build_prediction_scatter(model_bundle["prediction_frame"], target_column=target_column, lang=lang),
                    width="stretch",
                )

            st.markdown(
                section_header(
                    t(lang, "custom_prediction_title"),
                    t(lang, "custom_prediction_caption"),
                ),
                unsafe_allow_html=True,
            )

            genre_options = sorted(filtered_df["primary_genre"].dropna().astype(str).unique().tolist())
            studio_options = sorted(filtered_df["studio"].dropna().astype(str).unique().tolist())
            language_options = sorted(filtered_df["language"].dropna().astype(str).unique().tolist())

            with st.form("prediction_form"):
                col1, col2, col3, col4 = st.columns(4)
                budget = col1.number_input(
                    t(lang, "budget_usd"),
                    min_value=1_000_000.0,
                    value=float(filtered_df["budget"].median()),
                    step=5_000_000.0,
                )
                runtime = col2.number_input(
                    t(lang, "runtime_minutes"),
                    min_value=60,
                    max_value=220,
                    value=int(filtered_df["runtime"].median()),
                    step=1,
                )
                release_year = col3.slider(
                    t(lang, "release_year"),
                    min_value=int(cleaned_df["release_year"].min()),
                    max_value=int(cleaned_df["release_year"].max()) + 2,
                    value=int(filtered_df["release_year"].median()),
                )
                vote_count = col4.number_input(
                    t(lang, "current_view_count"),
                    min_value=0,
                    value=int(filtered_df["vote_count"].median()),
                    step=1000,
                )
                col5, col6, col7 = st.columns(3)
                metascore = col5.slider("Metascore", min_value=0, max_value=100, value=int(filtered_df["metascore"].median()))
                primary_genre = col6.selectbox(t(lang, "main_genre"), options=genre_options, index=0)
                studio = col7.selectbox(t(lang, "studio"), options=studio_options, index=0)
                language = st.selectbox(t(lang, "language_label"), options=language_options, index=0)
                submitted = st.form_submit_button(t(lang, "run_prediction"))

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
                predicted_views = predict_single(popularity_bundle, payload, target_column="vote_count")
                lead_text, trend_text, benchmark_text = build_prediction_summary(
                    target_column=target_column,
                    predicted_target=prediction,
                    predicted_views=predicted_views,
                    baseline_views=float(vote_count) if vote_count > 0 else None,
                    frame=filtered_df,
                    lang=lang,
                )

                st.success(lead_text)
                st.info(trend_text)
                st.warning(benchmark_text)

                comparison_col1, comparison_col2, comparison_col3 = st.columns(3)
                comparison_col1.metric(t(lang, "predicted_target"), format_target_value(prediction, target_column, lang))
                comparison_col2.metric(t(lang, "predicted_view_count"), f"{int(round(predicted_views)):,}")
                comparison_col3.metric(
                    t(lang, "expected_trend"),
                    compare_view_trend(predicted_views, float(vote_count) if vote_count > 0 else None, filtered_df).title(),
                )

                most_watched = filtered_df.sort_values(by="vote_count", ascending=False).iloc[0]
                least_watched = filtered_df.sort_values(by="vote_count", ascending=True).iloc[0]
                summary_frame = pd.DataFrame(
                    [
                        {
                            "Type": t(lang, "most_watched_movie"),
                            t(lang, "title"): most_watched["title"],
                            t(lang, "views"): int(most_watched["vote_count"]),
                            t(lang, "rating"): round(float(most_watched["rating"]), 1),
                        },
                        {
                            "Type": t(lang, "least_watched_movie"),
                            t(lang, "title"): least_watched["title"],
                            t(lang, "views"): int(least_watched["vote_count"]),
                            t(lang, "rating"): round(float(least_watched["rating"]), 1),
                        },
                        {
                            "Type": t(lang, "predicted_movie"),
                            t(lang, "title"): t(lang, "custom_input_movie"),
                            t(lang, "views"): int(round(predicted_views)),
                            t(lang, "rating"): round(float(prediction), 1) if target_column == "rating" else np.nan,
                        },
                    ]
                )
                st.dataframe(summary_frame, width="stretch")

                st.markdown(
                    section_header(
                        t(lang, "scenario_analysis"),
                        t(lang, "scenario_caption"),
                    ),
                    unsafe_allow_html=True,
                )
                scenario_frame = build_scenario_figure(model_bundle, payload, target_column=target_column)
                scenario_label = t(lang, "predicted_value")
                if target_column == "revenue":
                    scenario_label = t(lang, "predicted_revenue")
                elif target_column == "rating":
                    scenario_label = t(lang, "predicted_rating")
                elif target_column == "vote_count":
                    scenario_label = t(lang, "predicted_view_count_label")

                scenario_fig = px.line(
                    scenario_frame,
                    x="budget",
                    y="predicted",
                    text="scenario",
                    markers=True,
                    color_discrete_sequence=[PALETTE[4]],
                )
                scenario_fig.update_traces(line=dict(width=3), textposition="top center")
                scenario_fig.update_layout(xaxis_title=t(lang, "budget_usd"), yaxis_title=scenario_label)
                st.plotly_chart(style_figure(scenario_fig, height=360), width="stretch")
                st.dataframe(scenario_frame, width="stretch")

    with tabs[11]:
        st.markdown(
            section_header(
                t(lang, "data_explorer"),
                t(lang, "data_explorer_caption"),
            ),
            unsafe_allow_html=True,
        )
        raw_col, clean_col = st.columns(2)
        with raw_col:
            st.markdown(f"### {t(lang, 'raw_dataset')}")
            st.dataframe(raw_df.head(12), width="stretch")
        with clean_col:
            st.markdown(f"### {t(lang, 'cleaned_dataset')}")
            st.dataframe(cleaned_df.head(12), width="stretch")

        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.download_button(
                t(lang, "download_cleaned_csv"),
                data=cleaned_df.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_movie_dataset.csv",
                mime="text/csv",
            )
        with export_col2:
            st.download_button(
                t(lang, "download_filtered_csv"),
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_movie_dataset.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    if get_script_run_ctx() is None:
        print(t("vi", "this_is_streamlit_app"))
        print(r"  ..\.venv\Scripts\python.exe -m streamlit run app.py --browser.gatherUsageStats false")
        print(t("vi", "or_double_click"))
        sys.exit(0)
    main()
