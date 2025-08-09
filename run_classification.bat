@echo off
chcp 65001 >nul
echo PDF Standard Document Classification System
echo ===========================================

echo Checking environment...
python setup.py

echo.
echo Processing PDF files...
python main.py input_pdfs --output-dir jc

echo.
echo Processing completed!
echo Result files are in jc directory
echo Log file: pdf_classify.log
echo.
echo Press any key to continue...
pause >nul