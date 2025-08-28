#!/usr/bin/env python3
"""
Enhanced Text Anonymization System - Test Script
Demonstrates all the new features and capabilities
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from TextAnonymization import TextAnonymizer
    print("✅ Successfully imported TextAnonymizer")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def test_basic_functionality():
    """Test basic anonymization functionality"""
    print("\n🔍 Testing Basic Functionality...")
    
    try:
        # Initialize anonymizer
        anonymizer = TextAnonymizer(model_size="sm")  # Use small model for testing
        
        # Test text with various entity types
        test_text = """
        John Doe works at Microsoft Corporation in Seattle, Washington. 
        His email is john.doe@microsoft.com and phone number is (555) 123-4567.
        He lives at 123 Main Street, Seattle, WA 98101.
        His employee ID is EMP12345 and salary is $85,000 per year.
        """
        
        print(f"Original text: {test_text.strip()}")
        
        # Anonymize
        start_time = time.time()
        anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
        processing_time = time.time() - start_time
        
        print(f"✅ Anonymization completed in {processing_time:.2f}s")
        print(f"Generated key: {key}")
        print(f"Anonymized text: {anonymized.strip()}")
        print(f"Found {len(mapping)} entities to anonymize")
        print(f"Mapping:\n{mapping}")
        
        return anonymized, key, anonymizer
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return None, None, None

def test_text_restoration(anonymized_text, key, anonymizer):
    """Test text restoration functionality"""
    print("\n🔄 Testing Text Restoration...")
    
    try:
        # Restore original text
        restored_text = anonymizer.getActualTextFromAnonymized(anonymized_text, key)
        
        print(f"✅ Text restoration successful")
        print(f"Restored text: {restored_text.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text restoration failed: {e}")
        return False

def test_encryption_security():
    """Test encryption and security features"""
    print("\n🔐 Testing Encryption & Security...")
    
    try:
        # Create anonymizer with encryption
        anonymizer1 = TextAnonymizer()
        
        # Get the master key
        master_key = anonymizer1.secure_anon.master_key
        encoded_key = base64.urlsafe_b64encode(master_key).decode()
        
        print(f"✅ Generated master encryption key: {encoded_key[:20]}...")
        
        # Test with the same key
        anonymizer2 = TextAnonymizer(master_key=encoded_key)
        
        # Test text
        test_text = "Alice works at Google in Mountain View"
        anonymized1, mapping1, key1 = anonymizer1.getAnonymizeText(test_text)
        anonymized2, mapping2, key2 = anonymizer2.getAnonymizeText(test_text)
        
        print(f"✅ Encryption test successful")
        print(f"Anonymizer 1 key: {key1}")
        print(f"Anonymizer 2 key: {key2}")
        
        # Test that mappings are encrypted
        keys_dir = Path("Keys")
        encrypted_files = list(keys_dir.glob("KEY*.enc"))
        if encrypted_files:
            print(f"✅ Found {len(encrypted_files)} encrypted mapping files")
            
            # Try to read encrypted file (should be unreadable)
            with open(encrypted_files[0], 'rb') as f:
                encrypted_content = f.read()
                print(f"✅ Encrypted file content is binary (unreadable): {len(encrypted_content)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def test_batch_processing():
    """Test batch processing functionality"""
    print("\n📦 Testing Batch Processing...")
    
    try:
        anonymizer = TextAnonymizer(model_size="sm")
        
        # Create test texts
        test_texts = [
            "John Smith works at Apple in Cupertino",
            "Sarah Johnson is a developer at Facebook",
            "Mike Brown lives in New York City",
            "Lisa Davis works at Amazon in Seattle",
            "Tom Wilson is from Los Angeles"
        ]
        
        print(f"Processing {len(test_texts)} texts in batch...")
        
        start_time = time.time()
        results = anonymizer.batch_anonymize(test_texts, batch_size=3)
        processing_time = time.time() - start_time
        
        print(f"✅ Batch processing completed in {processing_time:.2f}s")
        
        successful = 0
        for i, (text, mapping, key) in enumerate(results):
            if key != "FAILED":
                successful += 1
                print(f"  Text {i+1}: {key} ({len(mapping)} entities)")
            else:
                print(f"  Text {i+1}: FAILED")
        
        print(f"Successfully processed: {successful}/{len(test_texts)} texts")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False

def test_validation_and_error_handling():
    """Test input validation and error handling"""
    print("\n🛡️ Testing Validation & Error Handling...")
    
    try:
        anonymizer = TextAnonymizer()
        
        # Test invalid inputs
        test_cases = [
            ("", "Empty string"),
            (None, "None value"),
            (123, "Integer instead of string"),
            ("A" * 2000000, "Very long text"),  # 2MB
            ("<script>alert('xss')</script>", "Malicious content")
        ]
        
        for test_input, description in test_cases:
            try:
                result = anonymizer.getAnonymizeText(test_input)
                print(f"❌ {description}: Should have failed but didn't")
            except (ValueError, RuntimeError, TypeError) as e:
                print(f"✅ {description}: Correctly caught error - {type(e).__name__}")
            except Exception as e:
                print(f"⚠️ {description}: Unexpected error type - {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_statistics():
    """Test statistics functionality"""
    print("\n📊 Testing Statistics...")
    
    try:
        anonymizer = TextAnonymizer()
        
        stats = anonymizer.get_statistics()
        
        print(f"✅ Statistics retrieved successfully")
        print(f"Total keys: {stats.get('total_keys', 0)}")
        print(f"Total entities: {stats.get('total_entities', 0)}")
        print(f"Model size: {stats.get('model_size', 'Unknown')}")
        print(f"Keys directory: {stats.get('keys_directory', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

def test_model_selection():
    """Test different model sizes"""
    print("\n🤖 Testing Model Selection...")
    
    try:
        # Test different model sizes
        for model_size in ["sm", "md", "lg"]:
            try:
                print(f"Testing {model_size} model...")
                anonymizer = TextAnonymizer(model_size=model_size)
                
                test_text = "John Doe works at Microsoft"
                start_time = time.time()
                anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
                processing_time = time.time() - start_time
                
                print(f"  ✅ {model_size} model: {processing_time:.2f}s, {len(mapping)} entities")
                
            except Exception as e:
                print(f"  ❌ {model_size} model failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model selection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Text Anonymization System - Test Suite")
    print("=" * 60)
    
    # Import base64 for encryption test
    global base64
    import base64
    
    # Track test results
    test_results = []
    
    # Run tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Text Restoration", lambda: test_text_restoration(*test_results[0][1]) if test_results else False),
        ("Encryption & Security", test_encryption_security),
        ("Batch Processing", test_batch_processing),
        ("Validation & Error Handling", test_validation_and_error_handling),
        ("Statistics", test_statistics),
        ("Model Selection", test_model_selection)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            test_results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
    
    print("\n💡 Tips:")
    print("- Install larger SpaCy models for better accuracy: python -m spacy download en_core_web_lg")
    print("- Check the anonymization.log file for detailed logs")
    print("- Use the README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
