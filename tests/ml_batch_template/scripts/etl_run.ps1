# etl_run.ps1
$EnvName = "prefect_env"      # change to your env
$Conda = "C:\Miniconda3\Scripts\activate.bat"
cmd /c "`"$Conda`" $EnvName && python C:\ml_project\flows\prefect_etl_flow.py"