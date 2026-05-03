# Mô hình xử lý dữ liệu (Data Model) & Pipeline của ứng dụng Phân tích dữ liệu phim

Tài liệu này trả lời trực tiếp câu hỏi khi báo cáo: **“Model xử lý dữ liệu phim của ứng dụng là gì?”**  
Trong ngữ cảnh bài này, “model” gồm 3 phần:

- **Mô hình dữ liệu (data model / schema)**: ứng dụng cần những cột nào, kiểu dữ liệu và ý nghĩa.
- **Pipeline xử lý dữ liệu (data processing pipeline)**: các bước chuẩn hoá + làm sạch + tạo đặc trưng (feature).
- **Mô hình dự đoán (ML model)**: thuật toán học máy, cách tiền xử lý cho mô hình, và các chỉ số đánh giá.

---

## 1) Mô hình dữ liệu phim (Schema)

Ứng dụng làm việc với dataset phim dạng bảng (Pandas DataFrame). Bộ cột **chuẩn (canonical columns)** mà app kỳ vọng:

### 1.1. Nhóm cột bắt buộc (Required)

| Cột | Kiểu dữ liệu mong muốn | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `title` | string | Tên phim | Nếu thiếu sẽ điền `"Untitled Film"` |
| `genres` | string | Thể loại, có thể nhiều giá trị | Chuẩn hoá về dạng `"Action, Drama"` |
| `studio` | string | Hãng phim / công ty sản xuất | Nếu thiếu sẽ điền `"Unknown"` |
| `language` | string | Ngôn ngữ gốc | Nếu thiếu sẽ điền `"Unknown"` |
| `rating` | float | Điểm đánh giá (0–10) | Clip về [0, 10] |
| `revenue` | float | Doanh thu (USD) | Clip tối thiểu 1,000,000 |
| `budget` | float | Ngân sách (USD) | Clip tối thiểu 1,000,000 |
| `runtime` | int | Thời lượng (phút) | Clip về [60, 220] |
| `release_year` | int | Năm phát hành | Clip về [1980, 2030] |
| `vote_count` | int | Số lượt đánh giá / proxy lượt xem | Clip tối thiểu 0 |
| `metascore` | int | Điểm phê bình (0–100) | Clip về [0, 100] |

### 1.2. Nhóm cột phát sinh (Derived / Feature Engineering)

| Cột | Công thức | Mục đích dùng ở dashboard |
|---|---|---|
| `primary_genre` | lấy thể loại đầu tiên trong `genres` | Nhóm/so sánh theo thể loại chính |
| `profit` | `revenue - budget` | KPI lợi nhuận |
| `roi` | `revenue / budget` | KPI hiệu quả đầu tư |

---

## 2) Pipeline xử lý dữ liệu (Data Processing Pipeline)

### “Pipeline” là gì?
**Pipeline** là “chuỗi bước xử lý” chạy theo thứ tự cố định: **Input → Chuẩn hoá → Làm sạch → Tạo đặc trưng → Phân tích/ML → Output**.  
Trong app này pipeline chính nằm ở `movie_analysis/data.py` và được gọi từ `app.py`.

### 2.1. Input dữ liệu
App nhận dữ liệu theo 2 cách:

- **Dữ liệu mẫu nội bộ**: `sample_data/movies_analysis_dataset.csv`  
- **Người dùng upload**: CSV hoặc Excel (`.csv`, `.xlsx`, `.xls`)

### 2.2. Chuẩn hoá tên cột (Column normalization)
Vì dữ liệu thực tế có thể đặt tên cột khác nhau, app dùng **alias map** để quy về schema chuẩn.

Ví dụ alias (rút gọn):
- `rating` có thể là: `vote_average`, `imdb_rating`, `score`, `diem`
- `revenue` có thể là: `box_office`, `gross`, `doanh_thu`
- `release_year` có thể suy ra từ `release_date`

Nếu thiếu cột bắt buộc, app **tự thêm cột** và để `NA` để xử lý ở bước làm sạch.

### 2.3. Làm sạch dữ liệu thiếu (Missing-value cleaning)
App chia làm 2 nhóm:

- **Cột số (numeric)**: `rating`, `revenue`, `budget`, `runtime`, `release_year`, `vote_count`, `metascore`  
  - Điền theo **`median`** (mặc định) hoặc **`mean`**.
  - Nếu cả cột rỗng: dùng **giá trị mặc định** (default) đã cấu hình trong code.

- **Cột chữ (categorical)**: `title`, `genres`, `studio`, `language`  
  - `title`: điền `"Untitled Film"`
  - Cột còn lại: điền theo **mode** hoặc hằng `"Unknown"` (tuỳ lựa chọn trên sidebar)

### 2.4. Chuẩn hoá thể loại (Genres normalization)
`genres` được chuẩn hoá về chuỗi duy nhất, phân tách bằng dấu phẩy và Title Case:

- Loại ký tự thừa như `[]`, `'`, `"`
- Chấp nhận nhiều kiểu phân tách: `| , ; /`
- Loại trùng thể loại trong cùng 1 phim

### 2.5. Loại bỏ dòng trùng lặp (Duplicate removal)
Nếu bật tuỳ chọn, app xoá duplicate dựa trên bộ khoá:
- `title` + `release_year` + `studio`

### 2.6. Ép kiểu và ràng buộc giá trị (Type casting & constraints)
Sau làm sạch, app ép kiểu và “clip” về khoảng hợp lý để ổn định biểu đồ và mô hình:

- `runtime`: int, [60, 220]
- `release_year`: int, [1980, 2030]
- `vote_count`: int, \(\ge 0\)
- `metascore`: int, [0, 100]
- `rating`: [0, 10]
- `budget`, `revenue`: \(\ge 1,000,000\)

### 2.7. Tạo đặc trưng (Feature engineering)
Tạo thêm:
- `primary_genre`
- `profit`
- `roi`

---

## 3) Báo cáo chất lượng dữ liệu (Data Quality Model)

App tạo “báo cáo chất lượng” để nói rõ dataset có đáng tin không:

- **Completeness**: tỷ lệ thiếu theo từng cột (missing %)
- **Outliers**: phát hiện outlier theo IQR cho các biến số (rating, revenue, budget, runtime, year, vote_count, metascore, profit, roi nếu có)
- **Invalid values**: đếm các giá trị sai quy tắc (rating ngoài 0–10, metascore ngoài 0–100, runtime quá ngắn, year ngoài range, …)
- **Duplicate rows**: số dòng trùng hoàn toàn trong raw dataset

---

## 4) Mô hình dự đoán (Machine Learning Model)

App hỗ trợ dự đoán 1 trong 3 mục tiêu:
- `revenue` (doanh thu)
- `rating` (điểm)
- `vote_count` (proxy lượt xem)

### 4.1. Tập đặc trưng đầu vào cho mô hình
Mô hình dùng các cột:
- Numeric: `budget`, `runtime`, `release_year`, `vote_count`, `metascore`
- Categorical: `primary_genre`, `studio`, `language`

Ghi chú: nếu dự đoán `vote_count` thì `vote_count` không được dùng làm feature (được tự loại khỏi feature set).

### 4.2. Preprocessing cho ML (ML pipeline)
Trước khi học máy, app dùng pipeline tiền xử lý:

- Numeric:
  - Imputer: median
  - StandardScaler
- Categorical:
  - Imputer: most_frequent
  - OneHotEncoder (handle_unknown="ignore")

### 4.3. Thuật toán (Model candidates)
App train và so sánh 3 mô hình hồi quy:
- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

### 4.4. Đánh giá mô hình
App đánh giá bằng:
- Train/Test split 80/20
- Cross-validation KFold (tối đa 5 folds, tự điều chỉnh theo kích thước dữ liệu)

Chỉ số hiển thị:
- \(R^2\)
- RMSE
- MAE
- CV_R2
- CV_RMSE

Sau đó app chọn **mô hình tốt nhất** theo trung bình CV \(R^2\), và vẽ:
- Scatter: actual vs predicted
- Feature importance (coef_ hoặc feature_importances_)

### 4.5. Dự đoán tuỳ chỉnh + scenario analysis
Trong tab Prediction, người dùng nhập form (budget, runtime, year, …).  
Ngoài kết quả dự đoán, app chạy **scenario analysis theo budget**: thay đổi budget theo các mức (70%, 85%, 100%, 115%, 130%) để xem dự đoán biến thiên.

---


