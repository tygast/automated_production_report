call C:\Users\user1\anaconda3\scripts\activate auto_reports
pushd %userprofile%\projects\automated_production_report\src\reports\controllers
call python run_report.py
call conda deactivate
popd