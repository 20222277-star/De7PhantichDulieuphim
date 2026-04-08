@echo off
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
echo.| "D:\baitap\.venv\Scripts\python.exe" -m streamlit run "D:\baitap\Phantichdulieuphim\app.py" --server.port 8510 --browser.gatherUsageStats false
