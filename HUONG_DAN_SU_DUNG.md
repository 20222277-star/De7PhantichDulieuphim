# Hướng Dẫn Sử Dụng Project Phân Tích Dữ Liệu Phim

Tài liệu này tổng hợp toàn bộ thông tin quan trọng của project: mục tiêu, công nghệ, chức năng, cách chạy, cách sử dụng từng phần, cấu trúc thư mục, dữ liệu đầu vào và các lưu ý khi demo/báo cáo.

## 1. Tên đề tài

Phân tích dữ liệu phim (Movie Analysis)

## 2. Mục tiêu của project

Project được xây dựng để đáp ứng đầy đủ các yêu cầu của đề tài:

1. Làm sạch dữ liệu thiếu.
2. Phân tích thể loại phim phổ biến.
3. Phân tích mối quan hệ giữa rating và doanh thu.
4. Trực quan hóa top phim.
5. Dự đoán rating hoặc doanh thu.

## 3. Công nghệ sử dụng

- `Python`: ngôn ngữ chính của project.
- `Streamlit`: xây dựng giao diện ứng dụng dạng dashboard.
- `Pandas`: đọc, xử lý và làm sạch dữ liệu.
- `NumPy`: hỗ trợ tính toán số học.
- `Plotly`: vẽ biểu đồ tương tác.
- `Scikit-learn`: huấn luyện mô hình dự đoán.
- `OpenPyXL`: hỗ trợ đọc file Excel.

## 4. Hình thức của ứng dụng

Đây là một ứng dụng web chạy cục bộ trên máy tính, không phải website triển khai công khai trên Internet.

Khi chạy ứng dụng, project sẽ mở ở địa chỉ:

- `http://localhost:8510`

## 5. Cách chạy project

### Cách đơn giản nhất

Mở thư mục project và nhấp đúp vào file:

- `run_app.bat`

### Cách chạy bằng terminal

```powershell
cd D:\baitap\Phantichdulieuphim
..\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8510 --browser.gatherUsageStats false
```

### Cổng mặc định

Ứng dụng được cố định ở cổng `8510` để tránh xung đột với Laravel hoặc các project web khác trên máy.

## 6. Chức năng chính của hệ thống

### 6.1. Sử dụng dữ liệu mẫu có sẵn

Ứng dụng có sẵn file dữ liệu mẫu để người dùng chạy demo ngay mà không cần chuẩn bị dataset riêng.

Chức năng này giúp:

- mở app lên là có dữ liệu để xem,
- thuận tiện khi demo với giảng viên,
- tránh lỗi do thiếu dữ liệu đầu vào.

### 6.2. Tải dữ liệu từ file CSV hoặc Excel

Người dùng có thể tải lên dữ liệu riêng bằng:

- file `.csv`
- file `.xlsx`
- file `.xls`

Mục đích:

- thay thế dữ liệu mẫu,
- phân tích dataset riêng,
- linh hoạt khi mở rộng bài báo cáo.

### 6.3. Làm sạch dữ liệu thiếu

Ứng dụng hỗ trợ xử lý dữ liệu thiếu ở hai nhóm:

- dữ liệu số,
- dữ liệu dạng chuỗi/phân loại.

Các tùy chọn xử lý:

- dữ liệu số: `median` hoặc `mean`,
- dữ liệu chữ: `mode` hoặc gán giá trị mặc định.

Ngoài ra ứng dụng còn:

- chuẩn hóa cột dữ liệu,
- tự bổ sung các cột còn thiếu nếu dataset không đủ chuẩn,
- loại bỏ dòng trùng lặp nếu người dùng bật chức năng này.

### 6.4. Lọc dữ liệu theo năm phát hành

Người dùng có thể chọn khoảng năm phát hành để chỉ xem các phim trong khoảng thời gian mong muốn.

Mục đích:

- tập trung phân tích theo giai đoạn,
- dễ quan sát xu hướng doanh thu và rating qua thời gian.

### 6.5. Lọc dữ liệu theo thể loại

Người dùng có thể chọn một hoặc nhiều thể loại phim.

Ví dụ:

- Action
- Drama
- Comedy
- Horror

Mục đích:

- chỉ phân tích nhóm phim cần quan tâm,
- hỗ trợ so sánh theo thể loại.

### 6.6. Hiển thị các chỉ số tổng quan

Ứng dụng hiển thị nhanh các thông tin:

- số lượng phim đang được xem,
- rating trung bình,
- tổng doanh thu,
- tương quan giữa rating và doanh thu.

Mục đích:

- giúp người dùng nắm nhanh bức tranh tổng thể của dataset hiện tại.

### 6.7. Phân tích dữ liệu thiếu trước và sau khi làm sạch

Ứng dụng có phần riêng để báo cáo:

- số lượng giá trị thiếu trước khi xử lý,
- số lượng giá trị thiếu sau khi xử lý,
- số dòng bị xóa do trùng lặp,
- cách ứng dụng điền dữ liệu thiếu.

Mục đích:

- chứng minh bước tiền xử lý dữ liệu,
- đáp ứng yêu cầu làm sạch dữ liệu của đề tài.

### 6.8. Phân tích thể loại phim phổ biến

Ứng dụng trực quan hóa số lượng phim theo từng thể loại.

Người dùng có thể biết:

- thể loại nào xuất hiện nhiều nhất,
- thể loại nào ít hơn,
- mức độ phổ biến của từng nhóm phim.

### 6.9. Phân tích hiệu suất thể loại

Ngoài số lượng, ứng dụng còn hỗ trợ so sánh:

- rating trung bình theo thể loại,
- doanh thu trung bình theo thể loại.

Mục đích:

- xem thể loại nào vừa phổ biến vừa hiệu quả về mặt doanh thu hoặc đánh giá.

### 6.10. Phân tích mối quan hệ giữa rating và doanh thu

Ứng dụng sử dụng biểu đồ phân tán để biểu diễn:

- rating trên một trục,
- doanh thu trên trục còn lại.

Ngoài ra còn có:

- đường xu hướng,
- hệ số tương quan Pearson,
- thông tin phim dẫn đầu doanh thu.

Mục đích:

- đánh giá phim rating cao có xu hướng doanh thu cao hay không.

### 6.11. Trực quan hóa top phim

Người dùng có thể xem top phim theo:

- doanh thu,
- rating,
- ngân sách.

Số lượng phim hiển thị có thể điều chỉnh, ví dụ:

- top 5,
- top 10,
- top 20.

Mục đích:

- phục vụ yêu cầu trực quan hóa top phim trong đề bài.

### 6.12. Huấn luyện mô hình dự đoán

Ứng dụng hỗ trợ dự đoán:

- doanh thu,
- hoặc rating.

Các mô hình được huấn luyện và so sánh:

- Linear Regression,
- Random Forest,
- Gradient Boosting.

Ứng dụng sẽ:

- huấn luyện mô hình,
- đo hiệu năng,
- chọn ra mô hình tốt nhất,
- hiển thị bảng kết quả.

### 6.13. Hiển thị chỉ số đánh giá mô hình

Phần dự đoán có hiển thị các chỉ số:

- `R2`
- `RMSE`
- `MAE`

Mục đích:

- đánh giá chất lượng dự đoán,
- phục vụ phần trình bày trong báo cáo.

### 6.14. Biểu đồ mức độ quan trọng của đặc trưng

Ứng dụng hiển thị biểu đồ feature importance để cho biết biến nào ảnh hưởng mạnh tới kết quả dự đoán.

Ví dụ các biến đầu vào:

- budget
- runtime
- release_year
- vote_count
- metascore
- primary_genre
- studio
- language

### 6.15. Dự đoán tùy chỉnh bằng form nhập liệu

Người dùng có thể nhập trực tiếp thông tin một bộ phim:

- ngân sách,
- thời lượng,
- năm phát hành,
- số lượt đánh giá,
- metascore,
- thể loại chính,
- hãng phim,
- ngôn ngữ.

Sau đó bấm nút dự đoán để nhận:

- doanh thu dự đoán,
- hoặc rating dự đoán.

### 6.16. Xem dữ liệu gốc và dữ liệu đã làm sạch

Ứng dụng có tab riêng để quan sát:

- raw dataset,
- cleaned dataset.

Mục đích:

- giúp so sánh dữ liệu trước và sau xử lý.

### 6.17. Tải dữ liệu đã xử lý

Người dùng có thể tải:

- file CSV sau khi làm sạch,
- file CSV sau khi áp dụng bộ lọc.

Mục đích:

- hỗ trợ xuất dữ liệu để đưa vào báo cáo hoặc phân tích tiếp.

## 7. Cách sử dụng từng phần trên giao diện

## 7.1. Sidebar

Thanh bên trái dùng để:

- tải file dữ liệu,
- chọn cách xử lý dữ liệu thiếu,
- bật/tắt xóa dòng trùng lặp,
- lọc theo năm,
- lọc theo thể loại.

### Cách dùng

1. Nếu chưa có dữ liệu riêng, không cần tải file.
2. Nếu có dữ liệu riêng, chọn `Upload CSV or Excel`.
3. Chọn cách xử lý dữ liệu số:
   - `median`
   - `mean`
4. Chọn cách xử lý dữ liệu chữ:
   - `mode`
   - `Unknown value`
5. Chọn có xóa dòng trùng lặp hay không.
6. Chọn khoảng năm phát hành.
7. Chọn thể loại cần phân tích.

## 7.2. Tab Overview

Tab này cho biết:

- bảng dữ liệu đang hiển thị,
- nguồn dữ liệu,
- insight tổng quan,
- các yêu cầu đề bài đã được đáp ứng.

### Khi nào dùng

- dùng để mở đầu khi demo,
- dùng để giới thiệu nhanh project.

## 7.3. Tab Cleaning

Tab này trình bày:

- số dòng trước và sau làm sạch,
- số dòng trùng lặp đã xóa,
- số cột được thêm,
- biểu đồ dữ liệu thiếu,
- bảng thống kê missing values.

### Khi nào dùng

- dùng để trình bày bước tiền xử lý dữ liệu.

## 7.4. Tab Genres

Tab này trình bày:

- biểu đồ số lượng phim theo thể loại,
- biểu đồ so sánh rating trung bình và doanh thu trung bình theo thể loại.

### Khi nào dùng

- dùng để trả lời câu hỏi thể loại nào phổ biến nhất.

## 7.5. Tab Rating vs Revenue

Tab này trình bày:

- biểu đồ phân tán,
- đường xu hướng,
- hệ số tương quan,
- phim doanh thu cao nhất.

### Khi nào dùng

- dùng để phân tích mối quan hệ giữa rating và doanh thu.

## 7.6. Tab Top Movies

Tab này cho phép:

- chọn tiêu chí xếp hạng,
- chọn số lượng top phim,
- xem biểu đồ và bảng top phim.

### Khi nào dùng

- dùng khi muốn trực quan hóa top 10 hoặc top 5 phim nổi bật.

## 7.7. Tab Prediction

Tab này dùng để:

- chọn mục tiêu dự đoán,
- xem bảng so sánh các mô hình,
- xem chỉ số đánh giá mô hình,
- xem biểu đồ feature importance,
- nhập dữ liệu để dự đoán.

### Cách dùng

1. Chọn `Prediction target` là `Revenue` hoặc `Rating`.
2. Xem mô hình tốt nhất.
3. Quan sát `R2`, `RMSE`, `MAE`.
4. Nhập dữ liệu ở phần `Custom prediction`.
5. Bấm `Run prediction`.

## 7.8. Tab Data Explorer

Tab này cho phép:

- xem dữ liệu gốc,
- xem dữ liệu đã làm sạch,
- tải file CSV đã làm sạch,
- tải file CSV đã lọc.

### Khi nào dùng

- dùng khi cần xuất dữ liệu ra ngoài hoặc kiểm tra chi tiết dataset.

## 8. Dữ liệu đầu vào của project

Project hỗ trợ dữ liệu phim với các cột chính sau:

- `title`
- `genres`
- `rating`
- `revenue`
- `budget`
- `runtime`
- `release_year`
- `vote_count`
- `metascore`
- `studio`
- `language`

## 9. Các file quan trọng trong project

- `app.py`: file chính điều khiển giao diện và luồng chạy.
- `movie_analysis/data.py`: đọc dữ liệu, chuẩn hóa cột, làm sạch dữ liệu.
- `movie_analysis/modeling.py`: huấn luyện mô hình và dự đoán.
- `movie_analysis/styles.py`: giao diện và CSS cho dashboard.
- `sample_data/movies_analysis_dataset.csv`: dữ liệu mẫu để demo.
- `run_app.bat`: file chạy nhanh trên Windows.
- `run_app.ps1`: file chạy trên PowerShell.
- `requirements.txt`: danh sách thư viện cần thiết.

## 10. Luồng hoạt động của ứng dụng

1. Người dùng chạy ứng dụng.
2. Ứng dụng đọc dữ liệu mẫu hoặc dữ liệu do người dùng tải lên.
3. Dữ liệu được chuẩn hóa tên cột.
4. Dữ liệu thiếu được xử lý.
5. Dữ liệu trùng lặp được loại bỏ nếu bật chức năng này.
6. Hệ thống tạo các biểu đồ phân tích.
7. Hệ thống huấn luyện mô hình dự đoán.
8. Giao diện hiển thị kết quả phân tích và dự đoán.

## 11. Điểm mạnh của project

- Giao diện đẹp, hiện đại, dễ demo.
- Có dữ liệu mẫu nên chạy ngay được.
- Đáp ứng đầy đủ yêu cầu đề bài.
- Có cả phần phân tích lẫn phần dự đoán.
- Có thể dùng dữ liệu riêng.
- Có thể xuất dữ liệu đã xử lý.

## 12. Cách demo ngắn gọn khi báo cáo

Thứ tự demo gợi ý:

1. Chạy ứng dụng bằng `run_app.bat`.
2. Giới thiệu tab `Overview`.
3. Chuyển sang `Cleaning` để trình bày bước làm sạch dữ liệu.
4. Chuyển sang `Genres` để nói về thể loại phim phổ biến.
5. Chuyển sang `Rating vs Revenue` để phân tích mối quan hệ giữa rating và doanh thu.
6. Chuyển sang `Top Movies` để trình bày top phim.
7. Chuyển sang `Prediction` để demo dự đoán.
8. Chuyển sang `Data Explorer` để cho thấy khả năng xuất dữ liệu.

## 13. Một số lỗi thường gặp

### 13.1. Nhấp vào `app.py` nhưng không chạy đúng

Nguyên nhân:

- đây là ứng dụng Streamlit, không phải file Python chạy trực tiếp như các bài lab thông thường.

Cách đúng:

- chạy `run_app.bat`

### 13.2. Không mở được ứng dụng trên trình duyệt

Kiểm tra địa chỉ:

- `http://localhost:8510`

### 13.3. Lo xung đột với Laravel

Ứng dụng này dùng cổng:

- `8510`

Laravel thường dùng:

- `8000`

Nên hai project sẽ không xung đột nếu Laravel vẫn ở cổng mặc định.

## 14. File nên dùng cho báo cáo

Nếu cần mô tả project trong báo cáo, nên dựa vào:

- `app.py`
- `movie_analysis/data.py`
- `movie_analysis/modeling.py`
- `sample_data/movies_analysis_dataset.csv`

## 15. Kết luận

Project này là một dashboard phân tích dữ liệu phim hoàn chỉnh, có khả năng làm sạch dữ liệu, trực quan hóa dữ liệu và dự đoán bằng học máy. Ứng dụng đáp ứng đầy đủ yêu cầu đề tài và phù hợp để demo, báo cáo và mở rộng thêm nếu cần.
