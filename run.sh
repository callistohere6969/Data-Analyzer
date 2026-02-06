#!/bin/bash
# Run the Multi-Agent Data Analyzer in projectvenv
# macOS/Linux shell script

echo "Activating projectvenv..."
source projectvenv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Could not activate projectvenv"
    exit 1
fi

echo "Installing/updating dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================"
echo "Running quick test..."
echo "============================================"
python quick_test.py

echo ""
echo "============================================"
echo "Test complete! Starting Streamlit app..."
echo "============================================"
echo ""
streamlit run app.py
