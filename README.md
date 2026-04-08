# Movie Analysis Dashboard

This project implements assignment topic 7: movie data analysis.

## Covered requirements

- Clean missing data
- Analyze popular movie genres
- Analyze the relationship between rating and revenue
- Visualize top movies
- Predict rating or revenue

## Main features

- Built-in sample dataset with realistic movie fields
- CSV and Excel upload support
- Data cleaning controls for missing values and duplicates
- Interactive filters by year and genre
- Modern dashboard UI with Plotly charts
- Regression models for revenue or rating prediction

## Run the app

```powershell
cd D:\baitap\Phantichdulieuphim
..\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8510 --browser.gatherUsageStats false
```

Or just run:

```powershell
cd D:\baitap\Phantichdulieuphim
.\run_app.ps1
```

The app is configured to use port `8510` by default to avoid conflicting with Laravel or other local services.

If your shell needs the full path wrapped in quotes, use:

```powershell
cd D:\baitap\Phantichdulieuphim
& "D:\baitap\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& "D:\baitap\.venv\Scripts\python.exe" -m streamlit run app.py --server.port 8510 --browser.gatherUsageStats false
```

## Suggested custom dataset columns

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
