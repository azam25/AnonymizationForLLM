#!/usr/bin/env python3
"""
Virtual Environment Setup Script for Enhanced Text Anonymization Library
Automates the creation of virtual environment and installation of dependencies
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"⚠️ {description} completed with warnings: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required, found {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def create_virtual_environment(venv_name="anonymization_env"):
    """Create a virtual environment"""
    print(f"\n🏗️ Creating virtual environment: {venv_name}")
    
    # Check if virtual environment already exists
    if os.path.exists(venv_name):
        print(f"⚠️ Virtual environment '{venv_name}' already exists")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print(f"🗑️ Removing existing virtual environment...")
            if platform.system() == "Windows":
                run_command(f"rmdir /s /q {venv_name}", "Removing existing virtual environment")
            else:
                run_command(f"rm -rf {venv_name}", "Removing existing virtual environment")
        else:
            print(f"✅ Using existing virtual environment: {venv_name}")
            return venv_name
    
    # Create virtual environment
    if run_command(f"python -m venv {venv_name}", f"Creating virtual environment '{venv_name}'"):
        print(f"✅ Virtual environment '{venvname}' created successfully")
        return venv_name
    else:
        print(f"❌ Failed to create virtual environment")
        return None

def get_activation_command(venv_name, platform_name):
    """Get the appropriate activation command for the platform"""
    if platform_name == "Windows":
        return f"{venv_name}\\Scripts\\activate"
    else:
        return f"source {venv_name}/bin/activate"

def install_dependencies(venv_name):
    """Install required dependencies in the virtual environment"""
    print(f"\n📦 Installing dependencies in virtual environment...")
    
    # Get platform-specific activation command
    platform_name = platform.system()
    activate_cmd = get_activation_command(venv_name, platform_name)
    
    # Upgrade pip
    if platform_name == "Windows":
        upgrade_cmd = f"{venv_name}\\Scripts\\python.exe -m pip install --upgrade pip"
    else:
        upgrade_cmd = f"{venv_name}/bin/pip install --upgrade pip"
    
    if not run_command(upgrade_cmd, "Upgrading pip in virtual environment"):
        print("⚠️ Pip upgrade failed, continuing...")
    
    # Install requirements
    if platform_name == "Windows":
        install_cmd = f"{venv_name}\\Scripts\\pip install -r requirements.txt"
    else:
        install_cmd = f"{venv_name}/bin/pip install -r requirements.txt"
    
    if not run_command(install_cmd, "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return False
    
    return True

def download_spacy_models(venv_name):
    """Download recommended SpaCy models"""
    print(f"\n🤖 Downloading SpaCy models...")
    
    platform_name = platform.system()
    
    # Get the appropriate python executable
    if platform_name == "Windows":
        python_cmd = f"{venv_name}\\Scripts\\python.exe"
    else:
        python_cmd = f"{venv_name}/bin/python"
    
    models = [
        ("en_core_web_sm", "Small model (fast, good accuracy)"),
        ("en_core_web_md", "Medium model (balanced speed/accuracy)"),
        ("en_core_web_lg", "Large model (slower, best accuracy) - RECOMMENDED"
    ]
    
    successful_downloads = 0
    
    for model, description in models:
        print(f"\n📥 Downloading {model} - {description}")
        download_cmd = f"{python_cmd} -m spacy download {model}"
        if run_command(download_cmd, f"Downloading {model}", check=False):
            successful_downloads += 1
        else:
            print(f"⚠️ Failed to download {model}, continuing with others...")
    
    if successful_downloads == 0:
        print("❌ No SpaCy models could be downloaded. The system may not work properly.")
        return False
    
    print(f"✅ Successfully downloaded {successful_downloads}/{len(models)} models")
    return True

def test_installation(venv_name):
    """Test if the installation was successful"""
    print(f"\n🧪 Testing installation...")
    
    platform_name = platform.system()
    
    # Get the appropriate python executable
    if platform_name == "Windows":
        python_cmd = f"{venv_name}\\Scripts\\python.exe"
    else:
        python_cmd = f"{venv_name}/bin/python"
    
    # Test import
    test_import_cmd = f"{python_cmd} -c \"from TextAnonymization import TextAnonymizer; print('Import successful')\""
    
    if run_command(test_import_cmd, "Testing import"):
        print("✅ Import test passed")
        return True
    else:
        print("❌ Import test failed")
        return False

def generate_commands(venv_name):
    """Generate the commands needed to run the test script"""
    print(f"\n📋 COMMANDS TO RUN TESTS")
    print("=" * 50)
    
    platform_name = platform.system()
    
    if platform_name == "Windows":
        print(f"\n# Activate virtual environment:")
        print(f"{venv_name}\\Scripts\\activate")
        
        print(f"\n# Run test script:")
        print(f"python test_library.py")
        
        print(f"\n# Or run with unittest module:")
        print(f"python -m unittest test_library.py -v")
        
        print(f"\n# Deactivate virtual environment when done:")
        print(f"deactivate")
        
    else:  # Unix/Linux/macOS
        print(f"\n# Activate virtual environment:")
        print(f"source {venv_name}/bin/activate")
        
        print(f"\n# Run test script:")
        print(f"python test_library.py")
        
        print(f"\n# Or run with unittest module:")
        print(f"python -m unittest test_library.py -v")
        
        print(f"\n# Deactivate virtual environment when done:")
        print(f"deactivate")
    
    print(f"\n# Alternative: Run tests in one command without activation:")
    if platform_name == "Windows":
        print(f"{venv_name}\\Scripts\\python.exe test_library.py")
    else:
        print(f"{venv_name}/bin/python test_library.py")

def main():
    """Main setup process"""
    print("🚀 Enhanced Text Anonymization Library - Virtual Environment Setup")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup cannot continue. Please upgrade Python.")
        return False
    
    # Get virtual environment name
    venv_name = input(f"\nEnter virtual environment name (default: anonymization_env): ").strip()
    if not venv_name:
        venv_name = "anonymization_env"
    
    # Create virtual environment
    if not create_virtual_environment(venv_name):
        print("\n❌ Failed to create virtual environment")
        return False
    
    # Install dependencies
    if not install_dependencies(venv_name):
        print("\n❌ Failed to install dependencies")
        return False
    
    # Download SpaCy models
    if not download_spacy_models(venv_name):
        print("\n⚠️ Some SpaCy models failed to download. The system may have limited functionality.")
    
    # Test installation
    if not test_installation(venv_name):
        print("\n❌ Installation test failed")
        return False
    
    print(f"\n🎉 Virtual environment setup completed successfully!")
    
    # Generate commands
    generate_commands(venv_name)
    
    print(f"\n💡 Next steps:")
    print(f"1. Activate the virtual environment using the command above")
    print(f"2. Run the test script: python test_library.py")
    print(f"3. Check the README.md for detailed documentation")
    print(f"4. Start using the enhanced anonymization system!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
