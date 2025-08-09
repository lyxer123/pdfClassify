@echo off
chcp 65001 >nul

echo ========================================
echo    PDF Document Classification System
echo ========================================
echo.

REM Check command line arguments
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="/?" goto show_help
if "%1"=="deploy" goto deploy_mode

echo [1/4] Check environment...
python setup.py
if errorlevel 1 (
    echo Error: Environment check failed
    echo Please install Python and dependencies
    pause
    exit /b 1
)
echo Environment check completed
echo.

echo [2/4] Prepare directories...
if not exist "input_pdfs" (
    mkdir input_pdfs
    echo Created input directory: input_pdfs
)
if not exist "jc" (
    mkdir jc
    echo Created output directory: jc
)

REM Check PDF files in input directory
set pdf_count=0
for %%f in (input_pdfs\*.pdf) do set /a pdf_count+=1

if %pdf_count%==0 (
    echo.
    echo No PDF files found in input_pdfs directory
    echo Please put PDF files in input_pdfs directory
    echo.
    echo Example:
    echo copy "C:\path\to\your\files\*.pdf" input_pdfs\
    echo.
    echo Other functions:
    echo %0 help    - Show help
    echo %0 deploy  - Deploy mode
    echo python main.py --demo - Run demo
    echo.
    pause
    exit /b 0
)

echo Found %pdf_count% PDF files
echo.

echo [3/4] Processing PDF files...
echo Input directory: input_pdfs
echo Output directory: jc
echo Mode: Standard mode (first 5 pages, 15s timeout)
echo.

python main.py input_pdfs --output-dir jc --verbose
if errorlevel 1 (
    echo.
    echo Error: PDF processing failed
    echo Check log file: pdf_classify.log
    echo.
    echo Common solutions:
    echo 1. Check if PDF files are corrupted
    echo 2. Ensure Tesseract OCR is working
    echo 3. Check memory and disk space
    echo 4. Try: python main.py --demo
    pause
    exit /b 1
)

echo.
echo [4/4] Processing completed!
echo ========================================
echo Matched PDF files copied to jc directory
echo Check detailed log: pdf_classify.log
echo Visualization: feature_visualization.png
echo ========================================
echo.

REM Show result statistics
if exist "jc\*.pdf" (
    set result_count=0
    for %%f in (jc\*.pdf) do set /a result_count+=1
    echo Processing results:
    echo Total input files: %pdf_count%
    echo Successful matches: %result_count%
    echo Success rate: approx %result_count%/%pdf_count%
) else (
    echo No files matched the standard template
    echo Please check if PDF files are standard documents
)

echo.
echo Other functions:
echo python test_features.py - Test feature extraction
echo python main.py --demo - Run demonstration
echo %0 help - Show help
echo %0 deploy - Deploy mode
echo.
echo Press any key to exit...
pause >nul
goto end

:deploy_mode
echo ========================================
echo    PDF Classification System - Deploy
echo ========================================
echo.

echo [1/3] Check environment...
python setup.py
if errorlevel 1 (
    echo Error: Environment check failed
    pause
    exit /b 1
)
echo Environment check completed
echo.

echo [2/3] Processing PDF files...
echo Input directory: input_pdfs
echo Output directory: jc
echo Mode: Deploy mode (skip file check)
echo.
python main.py input_pdfs --output-dir jc --verbose
if errorlevel 1 (
    echo Error: PDF processing failed
    pause
    exit /b 1
)

echo.
echo [3/3] Processing completed!
echo ========================================
echo Matched PDF files copied to jc directory
echo Check detailed log: pdf_classify.log
echo Visualization: feature_visualization.png
echo ========================================
echo.
echo Press any key to exit...
pause >nul
goto end

:show_help
echo.
echo PDF Document Classification System - Help
echo ==========================================
echo.
echo Basic usage:
echo %0            - Process PDF files in input_pdfs directory
echo %0 help       - Show this help information
echo %0 deploy     - Deploy mode (skip PDF file check)
echo.
echo Main commands:
echo python main.py                    - Process current directory
echo python main.py input_pdfs         - Process specified directory
echo python main.py --demo             - Run demonstration mode
echo python main.py --verbose          - Verbose output
echo python main.py --recursive        - Recursive search
echo.
echo Advanced options:
echo python main.py --output-dir DIR   - Specify output directory
echo python main.py --timeout 30       - Set timeout
echo python main.py --template FILE    - Use custom template
echo.
echo Test tools:
echo python setup.py                   - Environment check
echo python test_features.py           - Feature extraction test
echo python pdf_tools.py examples      - Usage examples
echo.
echo Toolkit:
echo python pdf_tools.py test FILE     - Test single PDF
echo python pdf_tools.py clean         - Clean misclassified files
echo python pdf_tools.py deploy        - One-click deployment
echo python pdf_tools.py monitor       - Start monitoring
echo.
echo Directory structure:
echo input_pdfs/         - Place PDF files to process
echo jc/                 - Matched PDF files output
echo pdf_classify.log    - Detailed processing log
echo templates/mb6.png   - Standard document template
echo.
echo System requirements:
echo - Python 3.7+
echo - Tesseract OCR (with Chinese language pack)
echo - Sufficient memory and disk space
echo.
pause

:end