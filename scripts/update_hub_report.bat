call C:\ProgramData\Anaconda3\scripts\activate auto_reports
pushd %USERPROFILE%\projects\automated_production_report
call git pull origin master
REM call conda env update --prefix ./env --file environment.yml  --prune
call pip install git+https://git.company.com/company_name/automated_production_report