@echo off
REM CSInterface.jsをダウンロードするスクリプト (Windows)

echo CSInterface.jsをダウンロードしています...

powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_10.x/CSInterface.js' -OutFile 'client\CSInterface.js'"

if %errorlevel% equ 0 (
    echo ✓ CSInterface.jsのダウンロードが完了しました
) else (
    echo ✗ ダウンロードに失敗しました
    exit /b 1
)

pause
