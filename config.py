"""
Enhanced Text Anonymization System - Configuration File
Customize system behavior and settings
"""

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Default SpaCy model size
# Options: 'sm' (fast, good), 'md' (balanced), 'lg' (best accuracy), 'trf' (excellent)
DEFAULT_MODEL_SIZE = "lg"

# Fallback model if preferred model is not available
FALLBACK_MODEL = "en_core_web_sm"

# =============================================================================
# ENCRYPTION CONFIGURATION
# =============================================================================

# Encryption algorithm (currently supports Fernet)
ENCRYPTION_ALGORITHM = "fernet"

# Key storage options
KEY_STORAGE_OPTIONS = {
    "env_var": "ANONYMIZATION_MASTER_KEY",
    "file_path": "~/.anonymization/master.key",
    "keyring": "anonymization_system"
}

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================

# Default batch size for batch processing
DEFAULT_BATCH_SIZE = 100

# Maximum number of worker threads for parallel processing
MAX_WORKERS = 4

# Memory limit for text processing (in bytes)
MAX_TEXT_SIZE = 1024 * 1024  # 1MB

# =============================================================================
# VALIDATION CONFIGURATION
# =============================================================================

# Input validation settings
VALIDATION_CONFIG = {
    "check_content_security": True,
    "max_text_length": MAX_TEXT_SIZE,
    "allowed_text_types": ["str"],
    "block_dangerous_patterns": True
}

# Dangerous content patterns to block
DANGEROUS_PATTERNS = [
    r'<script.*?>',           # Script tags
    r'javascript:',            # JavaScript protocol
    r'data:text/html',        # Data URLs
    r'vbscript:',             # VBScript protocol
    r'on\w+\s*=',             # Event handlers
    r'<iframe.*?>',           # Iframe tags
    r'<object.*?>',           # Object tags
    r'<embed.*?>',            # Embed tags
]

# =============================================================================
# ENTITY RECOGNITION CONFIGURATION
# =============================================================================

# Entity types to anonymize and their anonymization prefixes
ENTITY_MAPPING = {
    'PERSON': 'NAME',
    'GPE': 'LOCATION',        # Countries, cities, states
    'LOC': 'LOCATION',        # Non-GPE locations
    'FAC': 'LOCATION',        # Buildings, airports, highways
    'ORG': 'ORG',             # Organizations
    'NORP': 'ORG',            # Nationalities, religious or political groups
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

# Pattern-based anonymization settings
PATTERN_CONFIG = {
    'address': {
        'pattern': r'\d+\s[A-Za-z]+\s(St|Street|Rd|Road|Ave|Avenue|Blvd|Boulevard|Dr|Drive)',
        'prefix': 'ADDRESS',
        'min_length': 10
    },
    'id_pattern': {
        'pattern': r'\b[A-Za-z]?\d{2,}[A-Za-z0-9]*\b',
        'prefix': 'ID',
        'min_length': 3,
        'max_length': 15
    },
    'email': {
        'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'prefix': 'EMAIL',
        'min_length': 5
    },
    'phone': {
        'pattern': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'prefix': 'PHONE',
        'min_length': 10
    },
    'ssn': {
        'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
        'prefix': 'SSN',
        'min_length': 11
    },
    'credit_card': {
        'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'prefix': 'CREDIT_CARD',
        'min_length': 16
    },
    'ip_address': {
        'pattern': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'prefix': 'IP',
        'min_length': 7
    }
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "anonymization.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# =============================================================================
# STORAGE CONFIGURATION
# =============================================================================

# File storage settings
STORAGE_CONFIG = {
    "keys_directory": "Keys",
    "logs_directory": "logs",
    "backup_directory": "backups",
    "file_extension": ".enc",
    "metadata_extension": "_meta.json"
}

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Security settings
SECURITY_CONFIG = {
    "require_encryption": True,
    "key_rotation_enabled": False,
    "key_rotation_interval": 30,  # days
    "audit_logging": True,
    "access_control": False
}

# =============================================================================
# CUSTOMIZATION FUNCTIONS
# =============================================================================

def get_model_size():
    """Get the configured model size"""
    return DEFAULT_MODEL_SIZE

def get_batch_size():
    """Get the configured batch size"""
    return DEFAULT_BATCH_SIZE

def get_max_workers():
    """Get the maximum number of workers"""
    return MAX_WORKERS

def get_max_text_size():
    """Get the maximum text size limit"""
    return MAX_TEXT_SIZE

def get_entity_mapping():
    """Get the entity mapping configuration"""
    return ENTITY_MAPPING.copy()

def get_pattern_config():
    """Get the pattern configuration"""
    return PATTERN_CONFIG.copy()

def get_logging_config():
    """Get the logging configuration"""
    return LOGGING_CONFIG.copy()

def get_storage_config():
    """Get the storage configuration"""
    return STORAGE_CONFIG.copy()

def get_security_config():
    """Get the security configuration"""
    return SECURITY_CONFIG.copy()

# =============================================================================
# ENVIRONMENT OVERRIDES
# =============================================================================

def load_from_environment():
    """Load configuration from environment variables"""
    import os
    
    global DEFAULT_MODEL_SIZE, DEFAULT_BATCH_SIZE, MAX_WORKERS, MAX_TEXT_SIZE
    
    # Override with environment variables if present
    if os.getenv("ANONYMIZATION_MODEL_SIZE"):
        DEFAULT_MODEL_SIZE = os.getenv("ANONYMIZATION_MODEL_SIZE")
    
    if os.getenv("ANONYMIZATION_BATCH_SIZE"):
        try:
            DEFAULT_BATCH_SIZE = int(os.getenv("ANONYMIZATION_BATCH_SIZE"))
        except ValueError:
            pass
    
    if os.getenv("ANONYMIZATION_MAX_WORKERS"):
        try:
            MAX_WORKERS = int(os.getenv("ANONYMIZATION_MAX_WORKERS"))
        except ValueError:
            pass
    
    if os.getenv("ANONYMIZATION_MAX_TEXT_SIZE"):
        try:
            MAX_TEXT_SIZE = int(os.getenv("ANONYMIZATION_MAX_TEXT_SIZE"))
        except ValueError:
            pass

# Load environment overrides when module is imported
load_from_environment()

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Validate model size
    if DEFAULT_MODEL_SIZE not in ['sm', 'md', 'lg', 'trf']:
        errors.append(f"Invalid model size: {DEFAULT_MODEL_SIZE}")
    
    # Validate batch size
    if DEFAULT_BATCH_SIZE <= 0:
        errors.append(f"Invalid batch size: {DEFAULT_BATCH_SIZE}")
    
    # Validate max workers
    if MAX_WORKERS <= 0:
        errors.append(f"Invalid max workers: {MAX_WORKERS}")
    
    # Validate max text size
    if MAX_TEXT_SIZE <= 0:
        errors.append(f"Invalid max text size: {MAX_TEXT_SIZE}")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True

# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    print(f"Warning: Configuration validation failed: {e}")
    print("Using default values where possible.")
