#!/bin/bash
# Setup script for macOS/Linux
# Use with existing projectvenv

echo ""
echo "============================================"
echo "Multi-Agent Data Analyzer - Setup"
echo "============================================"
echo ""

echo "Step 1: Activating projectvenv..."
source projectvenv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Could not activate projectvenv"
    echo "Make sure projectvenv folder exists in the current directory"
    exit 1
fi

echo "Step 2: Installing dependencies..."
pip install -r requirements.txt --upgrade

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 3: Verifying setup..."

python -c "import streamlit; import pandas; import langchain; import langgraph; print('✓ All dependencies verified!')"

if [ $? -ne 0 ]; then
    echo "✗ Some dependencies are missing"
    exit 1
fi

echo ""
echo "Step 4: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "IMPORTANT: Edit .env and add your OpenRouter API key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenRouter API key"
echo "2. Run: ./run.sh"
echo "    OR"
echo "3. Manually: source projectvenv/bin/activate"
echo "           streamlit run app.py"
echo ""
