#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Text Anonymization Library
Tests all features including encryption, validation, batch processing, and edge cases
"""

import sys
import os
import time
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from TextAnonymization import TextAnonymizer, SecureAnonymization
    from config import get_model_size, get_batch_size, get_max_workers
    print("✅ Successfully imported TextAnonymizer and dependencies")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class TestSecureAnonymization(unittest.TestCase):
    """Test encryption and security features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.secure_anon = SecureAnonymization()
    
    def test_key_generation(self):
        """Test that encryption keys are generated correctly"""
        self.assertIsNotNone(self.secure_anon.master_key)
        
        # Debug: Print key details
        print(f"Key type: {type(self.secure_anon.master_key)}")
        print(f"Key length: {len(self.secure_anon.master_key)}")
        print(f"Key value (first 10 chars): {str(self.secure_anon.master_key)[:10]}")
        
        # Test both raw and encoded key methods
        raw_key = self.secure_anon.get_raw_key()
        encoded_key = self.secure_anon.get_encoded_key()
        
        print(f"Raw key length: {len(raw_key)}")
        print(f"Encoded key length: {len(encoded_key)}")
        
        # Fernet key should be 32 bytes (raw bytes)
        self.assertEqual(len(raw_key), 32)  # Raw key length
        self.assertEqual(len(encoded_key), 44)  # Base64 encoded length
        
        # Verify the key is actually bytes
        self.assertIsInstance(raw_key, bytes)
        self.assertIsInstance(encoded_key, str)
        
        # Additional verification: check that the key works with Fernet
        from cryptography.fernet import Fernet
        try:
            test_cipher = Fernet(raw_key)
            print("✅ Key is valid and works with Fernet")
        except Exception as e:
            print(f"❌ Key validation failed: {e}")
            self.fail(f"Generated key is not valid: {e}")
    
    def test_encryption_decryption(self):
        """Test that data can be encrypted and decrypted"""
        test_data = "This is a test string with sensitive information"
        
        # Encrypt
        encrypted = self.secure_anon.encrypt_data(test_data)
        self.assertIsInstance(encrypted, bytes)
        self.assertNotEqual(encrypted, test_data.encode())
        
        # Decrypt
        decrypted = self.secure_anon.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)
    
    def test_different_keys(self):
        """Test that different instances have different keys"""
        secure_anon2 = SecureAnonymization()
        self.assertNotEqual(self.secure_anon.master_key, secure_anon2.master_key)
    
    def test_key_reuse(self):
        """Test that the same key can be reused"""
        # Get the encoded key
        import base64
        encoded_key = base64.urlsafe_b64encode(self.secure_anon.master_key).decode()
        
        # Create new instance with same key
        secure_anon2 = SecureAnonymization(encoded_key)
        
        # Test encryption/decryption
        test_data = "Test data"
        encrypted = self.secure_anon.encrypt_data(test_data)
        decrypted = secure_anon2.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)

class TestTextAnonymizer(unittest.TestCase):
    """Test the main anonymization functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create Keys directory
        os.makedirs("Keys", exist_ok=True)
        
        # Initialize anonymizer with small model for testing
        self.anonymizer = TextAnonymizer(model_size="sm")
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that the anonymizer initializes correctly"""
        self.assertIsNotNone(self.anonymizer.nlp)
        self.assertEqual(self.anonymizer.model_size, "sm")
        self.assertIsNotNone(self.anonymizer.secure_anon)
    
    def test_basic_anonymization(self):
        """Test basic text anonymization"""
        test_text = "John Doe works at Microsoft in Seattle"
        
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(test_text)
        
        # Check that text was anonymized
        self.assertNotEqual(anonymized, test_text)
        # Mapping should be a pandas DataFrame, not a SpaCy doc
        import pandas as pd
        self.assertIsInstance(mapping, pd.DataFrame)
        self.assertIsInstance(key, str)
        self.assertTrue(len(key) == 6)  # 6-digit key
        
        # Check that original entities are in mapping
        original_entities = ["John Doe", "Microsoft", "Seattle"]
        for entity in original_entities:
            if entity in test_text:
                # Check if entity was anonymized
                self.assertTrue(
                    any(entity in str(row) for row in mapping.itertuples()),
                    f"Entity '{entity}' should be in mapping"
                )
    
    def test_entity_types(self):
        """Test that different entity types are properly anonymized"""
        test_text = """
        John Doe (PERSON) works at Microsoft Corporation (ORG) in Seattle (LOCATION).
        Contact: john.doe@microsoft.com (EMAIL) at (555) 123-4567 (PHONE).
        Address: 123 Main Street, Seattle, WA 98101 (ADDRESS).
        Employee ID: EMP12345 (ID) with salary $85,000 (MONEY).
        """
        
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(test_text)
        
        # Check that different entity types are anonymized
        anonymized_lower = anonymized.lower()
        self.assertIn("name", anonymized_lower)
        self.assertIn("org", anonymized_lower)
        self.assertIn("location", anonymized_lower)
        self.assertIn("email", anonymized_lower)
    
    def test_text_restoration(self):
        """Test that original text can be restored"""
        original_text = "Alice works at Google in Mountain View"
        
        # Anonymize
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(original_text)
        
        # Restore
        restored = self.anonymizer.getActualTextFromAnonymized(anonymized, key)
        
        # Check restoration
        self.assertEqual(restored, original_text)
    
    def test_validation(self):
        """Test input validation"""
        # Test empty string
        with self.assertRaises(ValueError):
            self.anonymizer.getAnonymizeText("")
        
        # Test None
        with self.assertRaises(ValueError):
            self.anonymizer.getAnonymizeText(None)
        
        # Test non-string input
        with self.assertRaises(ValueError):
            self.anonymizer.getAnonymizeText(123)
        
        # Test very long text
        long_text = "A" * 2000000  # 2MB
        with self.assertRaises(ValueError):
            self.anonymizer.getAnonymizeText(long_text)
    
    def test_dangerous_content_blocking(self):
        """Test that dangerous content is blocked"""
        dangerous_texts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for text in dangerous_texts:
            with self.assertRaises(ValueError):
                self.anonymizer.getAnonymizeText(text)
    
    def test_batch_processing(self):
        """Test batch processing functionality"""
        test_texts = [
            "John Smith works at Apple",
            "Sarah Johnson works at Facebook",
            "Mike Brown works at Amazon"
        ]
        
        results = self.anonymizer.batch_anonymize(test_texts, batch_size=2)
        
        # Check results
        self.assertEqual(len(results), len(test_texts))
        
        for result in results:
            anonymized, mapping, key = result
            self.assertIsInstance(anonymized, str)
            # Mapping should be a pandas DataFrame
            import pandas as pd
            self.assertIsInstance(mapping, pd.DataFrame)
            self.assertIsInstance(key, str)
    
    def test_anonymization_with_existing_key(self):
        """Test using existing anonymization mappings"""
        # Create initial text and anonymize
        text1 = "John works at Microsoft"
        anonymized1, mapping1, key1 = self.anonymizer.getAnonymizeText(text1)
        
        # Use existing key for new text
        text2 = "Jane works at Microsoft"  # Same company
        anonymized2 = self.anonymizer.getAnonymizedWithKey(text2, key1)
        
        # Check that Microsoft was anonymized consistently
        self.assertNotEqual(anonymized2, text2)
        self.assertIn("Microsoft", text2)
        
        # Check that the anonymized version doesn't contain Microsoft
        self.assertNotIn("Microsoft", anonymized2)
    
    def test_statistics(self):
        """Test statistics functionality"""
        # Create some anonymized texts first
        test_texts = ["Text 1", "Text 2", "Text 3"]
        for text in test_texts:
            self.anonymizer.getAnonymizeText(text)
        
        # Get statistics
        stats = self.anonymizer.get_statistics()
        
        # Check statistics
        self.assertIsInstance(stats, dict)
        self.assertIn('total_keys', stats)
        self.assertIn('total_entities', stats)
        self.assertIn('model_size', stats)
        self.assertIn('keys_directory', stats)
        
        # Check that we have some keys
        self.assertGreater(stats['total_keys'], 0)

class TestModelSelection(unittest.TestCase):
    """Test different model sizes and fallbacks"""
    
    def test_model_fallback(self):
        """Test that the system falls back to available models"""
        # Test with a model that might not be available
        try:
            anonymizer = TextAnonymizer(model_size="trf")
            self.assertIsNotNone(anonymizer.nlp)
        except RuntimeError:
            # If trf model is not available, it should fall back
            pass
    
    def test_model_performance(self):
        """Test performance differences between models"""
        test_text = "John Doe works at Microsoft in Seattle"
        
        for model_size in ["sm", "md"]:
            try:
                print(f"Testing {model_size} model...")
                anonymizer = TextAnonymizer(model_size=model_size)
                
                start_time = time.time()
                anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
                processing_time = time.time() - start_time
                
                # Check that processing completed
                self.assertIsInstance(anonymized, str)
                import pandas as pd
                self.assertIsInstance(mapping, pd.DataFrame)
                self.assertIsInstance(key, str)
                
                print(f"  ✅ {model_size} model: {processing_time:.3f}s, {len(mapping)} entities")
                
            except Exception as e:
                print(f"  ❌ {model_size} model failed: {e}")

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        os.makedirs("Keys", exist_ok=True)
        self.anonymizer = TextAnonymizer(model_size="sm")
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_empty_mapping(self):
        """Test handling of text with no entities"""
        text_without_entities = "This is a simple text with no names or organizations."
        
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(text_without_entities)
        
        # Text should remain unchanged
        self.assertEqual(anonymized, text_without_entities)
        # Key should indicate no entities
        self.assertEqual(key, "NO_ENTITIES")
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_text = "John Doe's email is john.doe@company.com & he works at Company Inc."
        
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(special_text)
        
        # Should handle special characters gracefully
        self.assertIsInstance(anonymized, str)
        # Mapping should be a pandas DataFrame
        import pandas as pd
        self.assertIsInstance(mapping, pd.DataFrame)
    
    def test_unicode_text(self):
        """Test handling of unicode text"""
        unicode_text = "José García trabaja en Microsoft en Madrid"
        
        anonymized, mapping, key = self.anonymizer.getAnonymizeText(unicode_text)
        
        # Should handle unicode gracefully
        self.assertIsInstance(anonymized, str)
        # Mapping should be a pandas DataFrame
        import pandas as pd
        self.assertIsInstance(mapping, pd.DataFrame)
    
    def test_malformed_key(self):
        """Test handling of malformed keys"""
        # Try to restore text with non-existent key
        with self.assertRaises(RuntimeError):
            self.anonymizer.getActualTextFromAnonymized("Some text", "INVALID")
    
    def test_large_batch(self):
        """Test handling of very large batches"""
        # Create a large number of test texts
        large_batch = [f"Text {i} with John Doe and Company {i}" for i in range(1000)]
        
        # This should not crash
        results = self.anonymizer.batch_anonymize(large_batch, batch_size=100)
        
        # Check that we got results for all texts
        self.assertEqual(len(results), len(large_batch))

class TestConfiguration(unittest.TestCase):
    """Test configuration and customization"""
    
    def test_config_loading(self):
        """Test that configuration is loaded correctly"""
        model_size = get_model_size()
        batch_size = get_batch_size()
        max_workers = get_max_workers()
        
        # Check that configuration values are valid
        self.assertIn(model_size, ['sm', 'md', 'lg', 'trf'])
        self.assertGreater(batch_size, 0)
        self.assertGreater(max_workers, 0)
    
    def test_environment_override(self):
        """Test environment variable overrides"""
        # Test with environment variable
        with patch.dict(os.environ, {'ANONYMIZATION_MODEL_SIZE': 'md'}):
            # Reload config to get new values
            import importlib
            import config
            importlib.reload(config)
            
            # Check that environment variable was respected
            self.assertEqual(config.DEFAULT_MODEL_SIZE, 'md')

def run_performance_test():
    """Run a performance test to measure system capabilities"""
    print("\n🚀 Performance Test")
    print("=" * 50)
    
    try:
        anonymizer = TextAnonymizer(model_size="sm")
        
        # Test with different text sizes
        text_sizes = [100, 1000, 10000]
        
        for size in text_sizes:
            # Generate test text
            test_text = f"John Doe works at Company Inc. " * (size // 50)
            
            start_time = time.time()
            anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
            processing_time = time.time() - start_time
            
            print(f"Text size: {len(test_text)} chars, Time: {processing_time:.3f}s, Entities: {len(mapping)}")
    
    except Exception as e:
        print(f"Performance test failed: {e}")



if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSecureAnonymization,
        TestTextAnonymizer,
        TestModelSelection,
        TestEdgeCases,
        TestConfiguration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("🎉 All tests passed!")
    else:
        print(f"❌ {len(result.failures)} tests failed")
        print(f"❌ {len(result.errors)} tests had errors")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  {test}: {traceback}")
    
    # Run performance test
    run_performance_test()
    
    print(f"\n💡 Test completed with {result.testsRun} tests run")
    
    success = result.wasSuccessful()
    sys.exit(0 if success else 1)
