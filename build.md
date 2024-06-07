

pyinstaller --clean --collect-all="xgboost" --collect-all="timspy" --collect-all="opentimspy" --collect-all="opentims_bruker_bridge" --add-data=".\resource\datasets;pyecharts\datasets\." --add-data=".\resource\templates;pyecharts\render\templates\." -i=./resource/logo/iDIAQC-logo.png -w .\main_applet.py -n diaqc_start
