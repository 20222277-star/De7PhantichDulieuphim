# Dashboard Phan Tich Du Lieu Phim

Project nay xay dung mot ung dung Streamlit de phan tich du lieu phim, lam sach du lieu, truc quan hoa insight va du doan doanh thu, rating hoac luot xem.

## Nguon Du Lieu

### Du lieu dang co san trong project

- App hien co san 2 bo du lieu noi bo trong thu muc `sample_data`:
- `sample_data/movies_analysis_dataset.csv`: bo du lieu mac dinh cua app
- `sample_data/movies_analysis_dataset_demo.csv`: bo du lieu demo bo sung de tai len va trinh bay rieng voi giang vien
- Ca hai bo du lieu nay deu do project tu tao de phuc vu demo, kiem thu giao dien, luong lam sach va mo hinh du doan.
- Khi nguoi dung tai file CSV hoac Excel rieng len, app se uu tien dung file do thay cho bo du lieu noi bo.

### Nguon goc bo du lieu noi bo

- Day khong phai la du lieu crawl truc tiep tu TMDb, OMDb hay IMDb.
- Du lieu duoc sinh tong hop trong code cua project tai `movie_analysis/data.py`.
- Cau truc cot duoc thiet ke theo schema du lieu phim pho bien de tuong thich voi du lieu that.

### Cach tao du lieu noi bo

Project sinh du lieu theo huong gan giong du lieu phim thuc te:

- tao ten phim gia lap
- gan 1 den 3 the loai cho moi phim
- sinh `budget`, `rating`, `runtime`, `vote_count`, `release_year`, `metascore`
- suy ra `revenue` theo ngan sach, do pho bien, diem so va yeu to ngau nhien
- chen mot phan gia tri thieu de mo phong du lieu ban
- chen them mot so dong trung de kiem thu buoc loai bo duplicate

### Nguon tham chieu nen dung cho du lieu that

- TMDb API la nguon tham chieu chinh phu hop nhat voi cau truc project hien tai:
- Trang chinh: https://developer.themoviedb.org/reference/getting-started
- Tim kiem va lay chi tiet phim: https://developer.themoviedb.org/docs/search-and-query-for-details
- Loc va kham pha phim theo dieu kien: https://developer.themoviedb.org/reference/discover-movie
- OMDb API co the dung de bo sung `Metascore` khi can:
- https://www.omdbapi.com/

### Cac truong du lieu phu hop voi project

CAC nguon tren phu hop de cung cap hoac suy ra cac truong ma app dang dung:

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

## Goi Y Demo Du Lieu

- Neu muon chay nhanh theo luong mac dinh cua app, dung `sample_data/movies_analysis_dataset.csv`.
- Neu muon demo thao tac tai file moi len he thong, dung `sample_data/movies_analysis_dataset_demo.csv`.
- Hai file deu giu cung schema nen toan bo cac tab phan tich, lam sach va du doan se hoat dong ngay sau khi tai len.

## Yeu Cau Da Dap Ung

- Lam sach du lieu thieu
- Phan tich the loai phim pho bien
- Phan tich moi quan he giua rating va doanh thu
- Truc quan hoa top phim
- Du doan rating hoac doanh thu

## Chuc Nang Chinh

- Dung san bo du lieu noi bo co cau truc giong du lieu phim thuc te
- Ho tro tai file CSV va Excel
- Lam sach du lieu thieu va loai bo dong trung lap
- Loc theo nam phat hanh va the loai
- Dashboard tuong tac voi bieu do Plotly
- Bao cao chat luong du lieu: missing, outlier, invalid values
- KPI mo rong: `profit`, `roi`
- Phan tich xu huong theo thoi gian
- Phan tich phan phoi va ma tran tuong quan
- So sanh 2 the loai hoac 2 hang phim
- Drill-down chi tiet tung phim
- Du doan bang nhieu mo hinh hoi quy va co scenario analysis
- Ho tro chuyen giao dien giua `Tieng Viet` va `English`

## Xu Ly Du Lieu

App hien thuc cac buoc xu ly du lieu chinh sau:

- Chuan hoa ten cot theo schema chung cua project
- Bo sung cac cot bat buoc neu du lieu dau vao con thieu
- Chuyen cac cot so ve dung kieu du lieu
- Xu ly missing cho du lieu so bang `median` hoac `mean`
- Xu ly missing cho du lieu chu bang `mode` hoac gia tri `Unknown`
- Tach va chuan hoa the loai phim
- Loai bo dong trung lap theo `title`, `release_year`, `studio`
- Tao them cac cot phan tich nhu `primary_genre`, `profit`, `roi`

## Tai Lieu Chi Tiet

Xem file `HUONG_DAN_SU_DUNG.md` de biet day du:

- danh sach chuc nang
- cach chay
- cach dung tung tab
- cau truc project
- ghi chu demo va bao cao

## Cach Chay Ung Dung

```powershell
cd D:\baitap\Phantichdulieuphim
..\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8510 --browser.gatherUsageStats false
```

Neu shell cua ban can duong dan day du:

```powershell
cd D:\baitap\Phantichdulieuphim
& "D:\baitap\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& "D:\baitap\.venv\Scripts\python.exe" -m streamlit run app.py --server.port 8510 --browser.gatherUsageStats false
```

Hoac chay nhanh bang:

```powershell
cd D:\baitap\Phantichdulieuphim
.\run_app.ps1
```

Ung dung mac dinh dung cong `8510` de tranh xung dot voi Laravel hoac cac dich vu cuc bo khac.
