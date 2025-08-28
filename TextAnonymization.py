import spacy
import random
import pandas as pd
import re
import string
import os
import io
import logging
from typing import List, Dict, Tuple, Optional, Union
from cryptography.fernet import Fernet
import base64
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('anonymization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecureAnonymization:
    """Handles encryption and decryption of mapping files"""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            try:
                self.master_key = base64.urlsafe_b64decode(master_key)
            except Exception as e:
                logger.error(f"Invalid master key format: {e}")
                raise ValueError("Invalid master key format")
        else:
            self.master_key = Fernet.generate_key()
            logger.info(f"Generated new master key: {base64.urlsafe_b64encode(self.master_key).decode()}")
        
        self.cipher = Fernet(self.master_key)
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt string data"""
        try:
            return self.cipher.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt encrypted data"""
        try:
            return self.cipher.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def get_encoded_key(self) -> str:
        """Get the base64 encoded version of the master key"""
        return base64.urlsafe_b64encode(self.master_key).decode()
    
    def get_raw_key(self) -> bytes:
        """Get the raw bytes of the master key"""
        return self.master_key

class TextAnonymizer:
    """Enhanced text anonymization with validation, encryption, and batch processing"""
    
    def __init__(self, model_size: str = "lg", master_key: Optional[str] = None):
        """
        Initialize the anonymizer
        
        Args:
            model_size: SpaCy model size ('sm', 'md', 'lg', 'trf')
            master_key: Optional master encryption key
        """
        self.model_size = model_size
        self.secure_anon = SecureAnonymization(master_key)
        
        # Load appropriate SpaCy model
        self._load_spacy_model()
        
        # Directory setup
        self.script_dir = Path(__file__).parent.absolute()
        self.keys_dir = self.script_dir / 'Keys'
        self.keys_dir.mkdir(exist_ok=True)
        
        # Validation patterns
        self._setup_validation_patterns()
        
        logger.info(f"TextAnonymizer initialized with {model_size} model")
    
    def _load_spacy_model(self):
        """Load the appropriate SpaCy model based on size preference"""
        model_map = {
            'sm': 'en_core_web_sm',
            'md': 'en_core_web_md', 
            'lg': 'en_core_web_lg',
            'trf': 'en_core_web_trf'
        }
        
        target_model = model_map.get(self.model_size, 'en_core_web_lg')
        
        try:
            self.nlp = spacy.load(target_model)
            logger.info(f"Successfully loaded SpaCy model: {target_model}")
        except OSError:
            logger.warning(f"Model {target_model} not found, falling back to en_core_web_sm")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("No SpaCy models available. Please install: python -m spacy download en_core_web_sm")
                raise RuntimeError("No SpaCy models available")
    
    def _setup_validation_patterns(self):
        """Setup regex patterns for validation and anonymization"""
        self.patterns = {
            'address': r'\d+\s[A-Za-z]+\s(St|Street|Rd|Road|Ave|Avenue|Blvd|Boulevard|Dr|Drive)',
            'id_pattern': r'\b[A-Za-z]?\d{2,}[A-Za-z0-9]*\b',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
    
    def validate_input(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate input text
        
        Args:
            text: Input text to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not text:
            errors.append("Input text cannot be empty")
            return False, errors
        
        if not isinstance(text, str):
            errors.append("Input must be a string")
            return False, errors
        
        if len(text.strip()) == 0:
            errors.append("Input text cannot be whitespace only")
            return False, errors
        
        if len(text) > 1000000:  # 1MB limit
            errors.append("Input text too large (max 1MB)")
            return False, errors
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            r'<script.*?>',  # Script tags
            r'javascript:',   # JavaScript protocol
            r'data:text/html' # Data URLs
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(f"Potentially dangerous content detected: {pattern}")
        
        return len(errors) == 0, errors
    
    def anonymize_entity(self, entity, doc) -> Tuple[str, Dict]:
        """Anonymize a single entity with enhanced logic"""
        # Check if already anonymized
        if re.match(r'^(NAME|LOCATION|ORG|EMAIL|ID|ADDRESS|PHONE|SSN|CREDIT_CARD|IP)\d{4}$', entity.text):
            return entity.text, {'Token': entity.text, 'Anonymized Value': entity.text}
        
        # Enhanced entity type mapping
        entity_mapping = {
            'PERSON': 'NAME',
            'GPE': 'LOCATION',  # Countries, cities, states
            'LOC': 'LOCATION',  # Non-GPE locations
            'FAC': 'LOCATION',  # Buildings, airports, highways
            'ORG': 'ORG',       # Organizations
            'NORP': 'ORG',      # Nationalities, religious or political groups
            'PRODUCT': 'PRODUCT',
            'EVENT': 'EVENT',
            'WORK_OF_ART': 'WORK_OF_ART',
            'LAW': 'LAW',
            'LANGUAGE': 'LANGUAGE',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'PERCENT': 'PERCENT',
            'MONEY': 'MONEY',
            'QUANTITY': 'QUANTITY',
            'ORDINAL': 'ORDINAL',
            'CARDINAL': 'CARDINAL'
        }
        
        entity_type = entity_mapping.get(entity.label_, 'OTHER')
        anonymized_value = f"{entity_type}{random.randint(1000, 9999)}"
        
        return anonymized_value, {
            'Token': entity.text,
            'Anonymized Value': anonymized_value,
            'Entity Type': entity.label_,
            'Confidence': entity.prob if hasattr(entity, 'prob') else None
        }
    
    def anonymize_patterns(self, text: str) -> Tuple[str, List[Dict]]:
        """Anonymize text using regex patterns"""
        mappings = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            for match in set(matches):
                if len(match) >= 3:  # Minimum length filter
                    anonymized_value = f"{pattern_name.upper()}{random.randint(1000, 9999)}"
                    mappings.append({
                        'Token': match,
                        'Anonymized Value': anonymized_value,
                        'Pattern Type': pattern_name
                    })
                    text = text.replace(match, anonymized_value, 1)
        
        return text, mappings
    
    def getAnonymizeText(self, text: str, save_flag: bool = True) -> Tuple[str, pd.DataFrame, str]:
        """
        Enhanced text anonymization with validation and encryption
        
        Args:
            text: Input text to anonymize
            save_flag: Whether to save the mapping
            
        Returns:
            Tuple of (anonymized_text, mapping_dataframe, generated_key)
        """
        start_time = time.time()
        
        # Input validation
        is_valid, errors = self.validate_input(text)
        if not is_valid:
            error_msg = "; ".join(errors)
            logger.error(f"Input validation failed: {error_msg}")
            raise ValueError(f"Input validation failed: {error_msg}")
        
        try:
            # Process text with SpaCy
            doc = self.nlp(text)
            
            # Collect all mappings
            all_mappings = []
            
            # Entity-based anonymization
            for ent in doc.ents:
                anonymized_value, mapping = self.anonymize_entity(ent, doc)
                all_mappings.append(mapping)
                text = text.replace(ent.text, anonymized_value, 1)
            
            # Pattern-based anonymization
            text, pattern_mappings = self.anonymize_patterns(text)
            all_mappings.extend(pattern_mappings)
            
            # Create mapping dataframe
            df = pd.DataFrame(all_mappings)
            
            if df.empty:
                logger.warning("No entities found to anonymize")
                return text, df, "NO_ENTITIES"
            
            # Generate key and save if requested
            generated_key = str(random.randint(100000, 999999))
            
            if save_flag:
                self._save_mapping(df, generated_key)
            
            processing_time = time.time() - start_time
            logger.info(f"Anonymization completed in {processing_time:.2f}s. Found {len(df)} entities.")
            
            return text, df, generated_key
            
        except Exception as e:
            logger.error(f"Anonymization failed: {e}")
            raise RuntimeError(f"Anonymization failed: {e}")
    
    def _save_mapping(self, df: pd.DataFrame, key: str):
        """Save encrypted mapping to file"""
        try:
            # Convert dataframe to CSV string
            csv_data = df.to_csv(index=False)
            
            # Encrypt the data
            encrypted_data = self.secure_anon.encrypt_data(csv_data)
            
            # Save encrypted file
            key_file = self.keys_dir / f"KEY{key}.enc"
            with open(key_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Save metadata
            metadata = {
                'key': key,
                'timestamp': time.time(),
                'entity_count': len(df),
                'model_used': self.model_size
            }
            
            metadata_file = self.keys_dir / f"KEY{key}_meta.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            logger.info(f"Mapping saved with key: {key}")
            
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")
            raise
    
    def getActualTextFromAnonymized(self, input_string: str, str_key: str) -> str:
        """
        Restore original text using stored key
        
        Args:
            input_string: Anonymized text
            str_key: Key to decrypt mapping
            
        Returns:
            Original text
        """
        try:
            # Load and decrypt mapping
            key_file = self.keys_dir / f"KEY{str_key}.enc"
            if not key_file.exists():
                raise FileNotFoundError(f"Key file not found: {str_key}")
            
            with open(key_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            csv_data = self.secure_anon.decrypt_data(encrypted_data)
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(csv_data))
            
            # Restore original text
            for _, row in df.iterrows():
                input_string = input_string.replace(row['Anonymized Value'], row['Token'])
            
            logger.info(f"Text restoration completed for key: {str_key}")
            return input_string
            
        except Exception as e:
            logger.error(f"Text restoration failed: {e}")
            raise RuntimeError(f"Text restoration failed: {e}")
    
    def getAnonymizedWithKey(self, text: str, key: str) -> str:
        """
        Apply existing anonymization mappings to new text
        
        Args:
            text: New text to anonymize
            key: Existing key to use
            
        Returns:
            Anonymized text
        """
        try:
            # Load existing mapping
            key_file = self.keys_dir / f"KEY{key}.enc"
            if not key_file.exists():
                raise FileNotFoundError(f"Key file not found: {key}")
            
            with open(key_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt existing mapping
            csv_data = self.secure_anon.decrypt_data(encrypted_data)
            existing_df = pd.read_csv(io.StringIO(csv_data))
            
            # Create mapping dictionary
            mapping_dict = dict(zip(existing_df['Token'], existing_df['Anonymized Value']))
            
            # Apply existing mappings
            for original_token, anonymized_value in mapping_dict.items():
                text = text.replace(original_token, anonymized_value)
            
            # Apply new anonymization for any remaining entities
            anonymized_text, new_df, _ = self.getAnonymizeText(text, save_flag=False)
            
            # Combine mappings
            combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Token']).reset_index(drop=True)
            
            # Save updated mapping
            self._save_mapping(combined_df, key)
            
            return anonymized_text
            
        except Exception as e:
            logger.error(f"Anonymization with key failed: {e}")
            raise RuntimeError(f"Anonymization with key failed: {e}")
    
    def batch_anonymize(self, texts: List[str], batch_size: int = 100) -> List[Tuple[str, pd.DataFrame, str]]:
        """
        Process multiple texts in batches for better performance
        
        Args:
            texts: List of texts to anonymize
            batch_size: Number of texts to process in parallel
            
        Returns:
            List of (anonymized_text, mapping_df, key) tuples
        """
        results = []
        
        # Validate inputs
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        logger.info(f"Starting batch processing of {len(texts)} texts with batch size {batch_size}")
        
        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Process batch in parallel
                with ThreadPoolExecutor(max_workers=min(batch_size, 4)) as executor:
                    future_to_text = {
                        executor.submit(self.getAnonymizeText, text, True): text 
                        for text in batch
                    }
                    
                    for future in as_completed(future_to_text):
                        try:
                            result = future.result()
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Batch processing failed for text: {e}")
                            # Add placeholder for failed processing
                            results.append(("", pd.DataFrame(), "FAILED"))
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise RuntimeError(f"Batch processing failed: {e}")
        
        logger.info(f"Batch processing completed. Successfully processed {len([r for r in results if r[2] != 'FAILED'])} texts")
        return results
    
    def get_statistics(self) -> Dict:
        """Get anonymization statistics"""
        try:
            key_files = list(self.keys_dir.glob("KEY*.enc"))
            total_keys = len(key_files)
            
            total_entities = 0
            for key_file in key_files:
                try:
                    with open(key_file, 'rb') as f:
                        encrypted_data = f.read()
                    csv_data = self.secure_anon.decrypt_data(encrypted_data)
                    df = pd.read_csv(io.StringIO(csv_data))
                    total_entities += len(df)
                except Exception as e:
                    logger.warning(f"Could not read key file {key_file}: {e}")
            
            return {
                'total_keys': total_keys,
                'total_entities': total_entities,
                'model_size': self.model_size,
                'keys_directory': str(self.keys_dir)
            }
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}

# Backward compatibility functions
def getAnonymizeText(text, savedFlag=0):
    """Legacy function for backward compatibility"""
    anonymizer = TextAnonymizer()
    return anonymizer.getAnonymizeText(text, save_flag=bool(savedFlag))

def getActualTextFromAnonymized(input_string, strKey):
    """Legacy function for backward compatibility"""
    anonymizer = TextAnonymizer()
    return anonymizer.getActualTextFromAnonymized(input_string, strKey)

def getAnonymizedWithKey(text, key):
    """Legacy function for backward compatibility"""
    anonymizer = TextAnonymizer()
    return anonymizer.getAnonymizedWithKey(text, key)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        # Initialize with larger model and encryption
        anonymizer = TextAnonymizer(model_size="lg")
        
        # Test text
        test_text = "John Doe works at Microsoft in Seattle. Contact: john.doe@microsoft.com"
        
        # Anonymize
        anonymized, mapping, key = anonymizer.getAnonymizeText(test_text)
        print(f"Original: {test_text}")
        print(f"Anonymized: {anonymized}")
        print(f"Key: {key}")
        print(f"Mapping:\n{mapping}")
        
        # Restore
        restored = anonymizer.getActualTextFromAnonymized(anonymized, key)
        print(f"Restored: {restored}")
        
        # Get statistics
        stats = anonymizer.get_statistics()
        print(f"Statistics: {stats}")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"Error: {e}")



