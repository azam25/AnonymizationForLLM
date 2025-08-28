#!/usr/bin/env python3
"""
Enhanced Text Anonymization System - Installation Script
Automates the setup process for the enhanced anonymization system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
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

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def download_spacy_models():
    """Download recommended SpaCy models"""
    print("\n🤖 Downloading SpaCy models...")
    
    models = [
        ("en_core_web_sm", "Small model (fast, good accuracy)"),
        ("en_core_web_md", "Medium model (balanced speed/accuracy)"),
        ("en_core_web_lg", "Large model (slower, best accuracy) - RECOMMENDED"
    ]
    
    successful_downloads = 0
    
    for model, description in models:
        print(f"\n📥 Downloading {model} - {description}")
        if run_command(f"python -m spacy download {model}", f"Downloading {model}"):
            successful_downloads += 1
        else:
            print(f"⚠️ Failed to download {model}, continuing with others...")
    
    if successful_downloads == 0:
        print("❌ No SpaCy models could be downloaded. The system may not work properly.")
        return False
    
    print(f"✅ Successfully downloaded {successful_downloads}/{len(models)} models")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    try:
        # Create Keys directory if it doesn't exist
        keys_dir = Path("Keys")
        keys_dir.mkdir(exist_ok=True)
        print("✅ Keys directory ready")
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        print("✅ Logs directory ready")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        # Try to import the main module
        from TextAnonymization import TextAnonymizer
        print("✅ TextAnonymizer imported successfully")
        
        # Try to create an instance
        anonymizer = TextAnonymizer(model_size="sm")
        print("✅ TextAnonymizer instance created successfully")
        
        # Test basic functionality
        test_text = "John Doe works at Microsoft"
        anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
        print("✅ Basic anonymization test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    examples = [
        ("Basic Usage", """
from TextAnonymization import TextAnonymizer

# Initialize
anonymizer = TextAnonymizer()

# Anonymize text
text = "John Doe works at Microsoft in Seattle"
anonymized, mapping, key = anonymizer.getAnonymizeText(text)

# Restore original text
restored = anonymizer.getActualTextFromAnonymized(anonymized, key)
        """),
        
        ("Batch Processing", """
# Process multiple texts
texts = ["Text 1", "Text 2", "Text 3"]
results = anonymizer.batch_anonymize(texts, batch_size=10)
        """),
        
        ("Advanced Configuration", """
# Use large model for better accuracy
anonymizer = TextAnonymizer(model_size="lg")

# Use existing encryption key
anonymizer = TextAnonymizer(master_key="your_key_here")
        """)
    ]
    
    for title, code in examples:
        print(f"\n{title}:")
        print(code.strip())

def main():
    """Main installation process"""
    print("🚀 Enhanced Text Anonymization System - Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Installation cannot continue. Please upgrade Python.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please check your internet connection and try again.")
        return False
    
    # Download SpaCy models
    if not download_spacy_models():
        print("\n⚠️ Some SpaCy models failed to download. The system may have limited functionality.")
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories. Please check permissions.")
        return False
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please check the error messages above.")
        return False
    
    print("\n🎉 Installation completed successfully!")
    
    # Show usage examples
    show_usage_examples()
    
    print("\n💡 Next steps:")
    print("1. Run the test suite: python test_enhanced.py")
    print("2. Check the README.md for detailed documentation")
    print("3. Start using the enhanced anonymization system!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
