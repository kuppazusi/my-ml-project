# train_run.ps1
$EnvName = "prefect_env"
$Conda = "C:\Miniconda3\Scripts\activate.bat"
cmd /c "`"$Conda`" $EnvName && mlflow run C:\ml_project\mlproject -e train -P n_estimators=200"