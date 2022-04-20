call C:\Users\user1\anaconda3\scripts\activate auto_reports
pushd %userprofile%\projects\automated_production_report\src\reports\spotfire
call python tank_measurement.py
call conda deactivate
popd