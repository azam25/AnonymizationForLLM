#!/bin/bash
# Unix/Linux/macOS Shell Script for Virtual Environment Setup
# Enhanced Text Anonymization Library

echo "🚀 Enhanced Text Anonymization Library - Unix/Linux/macOS Setup"
echo "=============================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "Please install Python 3.7+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python found"
$PYTHON_CMD --version

# Create virtual environment
echo ""
echo "🏗️ Creating virtual environment..."

if [ -d "anonymization_env" ]; then
    echo "⚠️ Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        echo "🗑️ Removing existing virtual environment..."
        rm -rf "anonymization_env"
    else
        echo "✅ Using existing virtual environment"
        goto_install_deps=true
    fi
fi

if [ "$goto_install_deps" != "true" ]; then
    $PYTHON_CMD -m venv anonymization_env
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created successfully"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
source anonymization_env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed successfully"

echo ""
echo "🤖 Downloading SpaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg
echo "✅ SpaCy models downloaded"

echo ""
echo "🧪 Testing installation..."
python -c "from TextAnonymization import TextAnonymizer; print('Import successful')"
if [ $? -ne 0 ]; then
    echo "❌ Installation test failed"
    exit 1
fi
echo "✅ Installation test passed"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 COMMANDS TO RUN TESTS:"
echo "========================="
echo ""
echo "# Activate virtual environment:"
echo "source anonymization_env/bin/activate"
echo ""
echo "# Run test script:"
echo "python test_library.py"
echo ""
echo "# Or run with unittest module:"
echo "python -m unittest test_library.py -v"
echo ""
echo "# Deactivate when done:"
echo "deactivate"
echo ""
echo "# Alternative: Run tests without activation:"
echo "anonymization_env/bin/python test_library.py"
echo ""
echo "💡 Next steps:"
echo "1. Activate the virtual environment using the command above"
echo "2. Run the test script: python test_library.py"
echo "3. Check the README.md for detailed documentation"
echo ""

# Deactivate virtual environment
deactivate
