@echo off 

rem 再帰呼び出しで表示されなくする
@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

rem バッチファイルのあるディレクトリに移動
cd /d %~dp0

rem ひとつ上のディレクトリに移動
cd ../

rem anacondaをアクティブにする
call C:\Users\3meko\miniconda3\Scripts\activate.bat

rem 仮想環境をアクティブにする
call activate scraping-env 

rem 検索＆フォロワーのツイートを取得
python app/favo_timeline.py

@REM pause