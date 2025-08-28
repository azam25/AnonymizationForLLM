@echo off
REM Windows Batch Script for Virtual Environment Setup
REM Enhanced Text Anonymization Library

echo 🚀 Enhanced Text Anonymization Library - Windows Setup
echo =====================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo.
echo 🏗️ Creating virtual environment...
if exist "anonymization_env" (
    echo ⚠️ Virtual environment already exists
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "%recreate%"=="y" (
        echo 🗑️ Removing existing virtual environment...
        rmdir /s /q "anonymization_env"
    ) else (
        echo ✅ Using existing virtual environment
        goto :install_deps
    )
)

python -m venv anonymization_env
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created successfully

:install_deps
echo.
echo 📦 Installing dependencies...
call anonymization_env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully

echo.
echo 🤖 Downloading SpaCy models...
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg
echo ✅ SpaCy models downloaded

echo.
echo 🧪 Testing installation...
python -c "from TextAnonymization import TextAnonymizer; print('Import successful')"
if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)
echo ✅ Installation test passed

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 COMMANDS TO RUN TESTS:
echo =========================
echo.
echo # Activate virtual environment:
echo anonymization_env\Scripts\activate
echo.
echo # Run test script:
echo python test_library.py
echo.
echo # Or run with unittest module:
echo python -m unittest test_library.py -v
echo.
echo # Deactivate when done:
echo deactivate
echo.
echo # Alternative: Run tests without activation:
echo anonymization_env\Scripts\python.exe test_library.py
echo.
echo 💡 Next steps:
echo 1. Activate the virtual environment using the command above
echo 2. Run the test script: python test_library.py
echo 3. Check the README.md for detailed documentation
echo.
pause
