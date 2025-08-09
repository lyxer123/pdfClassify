#!/bin/bash

# PDF Document Classification System
# Combined script supporting multiple modes

echo "========================================="
echo "   PDF Document Classification System"
echo "========================================="
echo

# Check command line arguments
show_help() {
    echo
    echo "PDF Document Classification System - Help"
    echo "=========================================="
    echo
    echo "Basic usage:"
    echo "  $0              # Process PDF files in input_pdfs directory"
    echo "  $0 help         # Show this help information"
    echo "  $0 deploy       # Deploy mode (simplified output)"
    echo
    echo "Main commands:"
    echo "  python3 main.py                    # Process current directory"
    echo "  python3 main.py input_pdfs         # Process specified directory"
    echo "  python3 main.py --demo             # Run demonstration mode"
    echo "  python3 main.py --verbose          # Verbose output"
    echo "  python3 main.py --recursive        # Recursive search"
    echo
    echo "Advanced options:"
    echo "  python3 main.py --output-dir DIR   # Specify output directory"
    echo "  python3 main.py --timeout 30       # Set timeout"
    echo "  python3 main.py --template FILE    # Use custom template"
    echo
    echo "Test tools:"
    echo "  python3 setup.py                   # Environment check"
    echo "  python3 test_features.py           # Feature extraction test"
    echo "  python3 pdf_tools.py examples      # Usage examples"
    echo
    echo "Toolkit:"
    echo "  python3 pdf_tools.py test FILE     # Test single PDF"
    echo "  python3 pdf_tools.py clean         # Clean misclassified files"
    echo "  python3 pdf_tools.py deploy        # One-click deployment"
    echo "  python3 pdf_tools.py monitor       # Start monitoring"
    echo
    echo "Directory structure:"
    echo "  input_pdfs/         # Place PDF files to process"
    echo "  jc/                 # Matched PDF files output"
    echo "  pdf_classify.log    # Detailed processing log"
    echo "  templates/mb6.png   # Standard document template"
    echo
    echo "System requirements:"
    echo "  - Python 3.7+"
    echo "  - Tesseract OCR (with Chinese language pack)"
    echo "  - Sufficient memory and disk space"
    echo
    exit 0
}

deploy_mode() {
    echo "========================================="
    echo "   PDF Classification System - Deploy"
    echo "========================================="
    echo

    echo "[1/3] Check environment..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "Error: Environment check failed"
        exit 1
    fi
    echo "✓ Environment check completed"
    echo

    echo "[2/3] Processing PDF files..."
    echo "Input directory: input_pdfs"
    echo "Output directory: jc"
    echo "Mode: Deploy mode (simplified output)"
    echo
    python3 main.py input_pdfs --output-dir jc --verbose
    if [ $? -ne 0 ]; then
        echo "Error: PDF processing failed"
        exit 1
    fi

    echo
    echo "[3/3] Processing completed!"
    echo "========================================="
    echo "✓ Matched PDF files copied to jc directory"
    echo "✓ Check detailed log: pdf_classify.log"
    echo "✓ Visualization: feature_visualization.png"
    echo "========================================="
    exit 0
}

# Handle command line arguments
case "$1" in
    "help"|"--help"|"-h")
        show_help
        ;;
    "deploy")
        deploy_mode
        ;;
esac

# Standard mode (default)
echo "[1/4] Check environment..."
python3 setup.py
if [ $? -ne 0 ]; then
    echo "Error: Environment check failed"
    echo
    echo "Solutions:"
    echo "1. Ensure Python 3.7+ is installed"
    echo "2. Run: pip3 install -r requirements.txt"
    echo "3. Install Tesseract OCR with Chinese language pack"
    exit 1
fi
echo "✓ Environment check completed"
echo

echo "[2/4] Prepare directories..."
if [ ! -d "input_pdfs" ]; then
    mkdir -p input_pdfs
    echo "✓ Created input directory: input_pdfs"
fi
if [ ! -d "jc" ]; then
    mkdir -p jc
    echo "✓ Created output directory: jc"
fi

# Check PDF files in input directory
pdf_count=$(find input_pdfs -name "*.pdf" -type f 2>/dev/null | wc -l)

if [ $pdf_count -eq 0 ]; then
    echo
    echo "📄 No PDF files found in input_pdfs directory"
    echo "Please put PDF files in input_pdfs directory"
    echo
    echo "Example:"
    echo "  cp /path/to/your/files/*.pdf input_pdfs/"
    echo
    echo "💡 Other functions:"
    echo "  $0 help     - Show help"
    echo "  $0 deploy   - Deploy mode"
    echo "  python3 main.py --demo - Run demo"
    echo
    exit 0
fi

echo "✓ Found $pdf_count PDF files"
echo

echo "[3/4] Processing PDF files..."
echo "Input directory: input_pdfs"
echo "Output directory: jc"
echo "Mode: Standard mode (first 5 pages, 15s timeout)"
echo

python3 main.py input_pdfs --output-dir jc --verbose
if [ $? -ne 0 ]; then
    echo
    echo "Error: PDF processing failed"
    echo "Check log file: pdf_classify.log"
    echo
    echo "Common solutions:"
    echo "1. Check if PDF files are corrupted"
    echo "2. Ensure Tesseract OCR is working"
    echo "3. Check memory and disk space"
    echo "4. Try: python3 main.py --demo"
    exit 1
fi

echo
echo "[4/4] Processing completed!"
echo "========================================="
echo "✓ Matched PDF files copied to jc directory"
echo "✓ Check detailed log: pdf_classify.log"
echo "✓ Visualization: feature_visualization.png"
echo "========================================="
echo

# Show result statistics
result_count=$(find jc -name "*.pdf" -type f 2>/dev/null | wc -l)
if [ $result_count -gt 0 ]; then
    echo "📊 Processing results:"
    echo "   Total input files: $pdf_count"
    echo "   Successful matches: $result_count"
    echo "   Success rate: approx $result_count/$pdf_count"
else
    echo "⚠️  No files matched the standard template"
    echo "   Please check if PDF files are standard documents"
fi

echo
echo "💡 Other functions:"
echo "   python3 test_features.py - Test feature extraction"
echo "   python3 main.py --demo - Run demonstration"
echo "   $0 help - Show help"
echo "   $0 deploy - Deploy mode"
echo

exit 0
