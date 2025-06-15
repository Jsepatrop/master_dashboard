"""
Cryptographic utilities for Master Dashboard Agent
Provides secure machine identification, data encryption, and authentication utilities
"""
import hashlib
import secrets
import uuid
import platform
import socket
from pathlib import Path
from typing import Optional, Dict, Any
import json
import base64
import hmac
import time

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

class CryptoUtils:
    """Cryptographic utilities for the agent"""
    
    @staticmethod
    def generate_machine_id() -> str:
        """
        Generate a unique machine ID based on hardware characteristics
        This creates a consistent ID that persists across agent restarts
        """
        # Collect machine-specific information
        machine_info = [
            platform.node(),  # Hostname
            platform.machine(),  # Architecture
            platform.processor(),  # Processor
            str(uuid.getnode()),  # MAC address
        ]
        
        # Try to get additional unique identifiers
        try:
            # Get primary network interface MAC
            import psutil
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK and addr.address != '00:00:00:00:00:00':
                        machine_info.append(addr.address)
                        break
        except:
            pass
        
        # Create hash of machine information
        machine_string = '|'.join(filter(None, machine_info))
        machine_hash = hashlib.sha256(machine_string.encode()).hexdigest()
        
        # Format as UUID-like string
        return f"agent-{machine_hash[:8]}-{machine_hash[8:12]}-{machine_hash[12:16]}-{machine_hash[16:20]}-{machine_hash[20:32]}"
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a session token with timestamp"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_urlsafe(16)
        return f"{timestamp}.{random_part}"
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Use PBKDF2 with SHA256
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key, salt
    
    @staticmethod
    def verify_password(password: str, key: bytes, salt: bytes) -> bool:
        """Verify a password against its hash"""
        test_key, _ = CryptoUtils.hash_password(password, salt)
        return hmac.compare_digest(key, test_key)
    
    @staticmethod
    def create_signature(data: str, secret: str) -> str:
        """Create HMAC signature for data"""
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        expected_signature = CryptoUtils.create_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)

class SecureStorage:
    """Secure storage for sensitive configuration data"""
    
    def __init__(self, storage_path: str, password: Optional[str] = None):
        self.storage_path = Path(storage_path)
        self.password = password
        self._key = None
        
        if CRYPTOGRAPHY_AVAILABLE and password:
            self._setup_encryption(password)
    
    def _setup_encryption(self, password: str):
        """Setup encryption key from password"""
        salt = b'master_dashboard_salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self._key = Fernet(key)
    
    def store_data(self, data: Dict[str, Any]) -> bool:
        """Store data securely"""
        try:
            json_data = json.dumps(data, indent=2)
            
            if self._key and CRYPTOGRAPHY_AVAILABLE:
                # Encrypt data
                encrypted_data = self._key.encrypt(json_data.encode())
                self.storage_path.write_bytes(encrypted_data)
            else:
                # Store as plain text (not recommended for production)
                self.storage_path.write_text(json_data)
            
            return True
        except Exception as e:
            print(f"Error storing data: {e}")
            return False
    
    def load_data(self) -> Optional[Dict[str, Any]]:
        """Load data securely"""
        try:
            if not self.storage_path.exists():
                return None
            
            if self._key and CRYPTOGRAPHY_AVAILABLE:
                # Decrypt data
                encrypted_data = self.storage_path.read_bytes()
                decrypted_data = self._key.decrypt(encrypted_data)
                json_data = decrypted_data.decode()
            else:
                # Load plain text
                json_data = self.storage_path.read_text()
            
            return json.loads(json_data)
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

class TokenManager:
    """Manages authentication tokens and their lifecycle"""
    
    def __init__(self, storage_path: str):
        self.storage = SecureStorage(storage_path)
        self.tokens = self.storage.load_data() or {}
    
    def generate_token(self, identifier: str, ttl: int = 3600) -> str:
        """Generate a new token with expiration"""
        token = CryptoUtils.generate_session_token()
        expiry = int(time.time()) + ttl
        
        self.tokens[identifier] = {
            'token': token,
            'expiry': expiry,
            'created': int(time.time())
        }
        
        self._save_tokens()
        return token
    
    def validate_token(self, identifier: str, token: str) -> bool:
        """Validate a token"""
        if identifier not in self.tokens:
            return False
        
        stored_token = self.tokens[identifier]
        
        # Check if token matches
        if not hmac.compare_digest(stored_token['token'], token):
            return False
        
        # Check if token is expired
        if time.time() > stored_token['expiry']:
            self.revoke_token(identifier)
            return False
        
        return True
    
    def refresh_token(self, identifier: str, ttl: int = 3600) -> Optional[str]:
        """Refresh an existing token"""
        if identifier in self.tokens:
            return self.generate_token(identifier, ttl)
        return None
    
    def revoke_token(self, identifier: str) -> bool:
        """Revoke a token"""
        if identifier in self.tokens:
            del self.tokens[identifier]
            self._save_tokens()
            return True
        return False
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        current_time = time.time()
        expired_identifiers = [
            identifier for identifier, data in self.tokens.items()
            if current_time > data['expiry']
        ]
        
        for identifier in expired_identifiers:
            del self.tokens[identifier]
        
        if expired_identifiers:
            self._save_tokens()
    
    def _save_tokens(self):
        """Save tokens to storage"""
        self.storage.store_data(self.tokens)

# Utility functions for common operations
def generate_machine_id() -> str:
    """Generate unique machine identifier"""
    return CryptoUtils.generate_machine_id()

def create_machine_fingerprint() -> Dict[str, Any]:
    """Create detailed machine fingerprint for identification"""
    fingerprint = {
        'machine_id': generate_machine_id(),
        'hostname': platform.node(),
        'system': platform.system(),
        'release': platform.release(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'timestamp': int(time.time())
    }
    
    # Add network information
    try:
        fingerprint['ip_address'] = socket.gethostbyname(socket.gethostname())
    except:
        fingerprint['ip_address'] = 'unknown'
    
    # Add MAC address
    try:
        fingerprint['mac_address'] = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                             for elements in range(0,2*6,2)][::-1])
    except:
        fingerprint['mac_address'] = 'unknown'
    
    return fingerprint

def secure_compare(a: str, b: str) -> bool:
    """Secure string comparison to prevent timing attacks"""
    return hmac.compare_digest(a.encode(), b.encode())

def generate_nonce(length: int = 16) -> str:
    """Generate a cryptographic nonce"""
    return secrets.token_hex(length)

def create_checksum(data: str) -> str:
    """Create SHA-256 checksum of data"""
    return hashlib.sha256(data.encode()).hexdigest()

def verify_checksum(data: str, expected_checksum: str) -> bool:
    """Verify data against expected checksum"""
    actual_checksum = create_checksum(data)
    return hmac.compare_digest(actual_checksum, expected_checksum)