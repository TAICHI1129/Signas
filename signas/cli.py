"""
Signas - Secure File Digital Signature Tool
Author: TAICHI1129
License: MIT
"""

import hashlib
import sys
import os
import json
import base64
import getpass
from datetime import datetime
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Constants
CHUNK_SIZE = 65536  # 64KB
MIN_PASSWORD_LENGTH = 12
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"
AUDIT_LOG_FILE = "audit.log"


# --- Logging function ---
def write_log(action: str, filepath: str, status: str, details: str = "") -> None:
    """
    Records actions to audit.log.
    
    Args:
        action: The action performed (GENKEY, SIGN, VERIFY, HASH)
        filepath: The file being processed
        status: SUCCESS or FAILED
        details: Additional information about the operation
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ACTION: {action} | FILE: {filepath} | STATUS: {status} | {details}\n"
    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Warning: Could not write to audit log: {e}")


# --- Key Management ---
def generate_keys() -> None:
    """
    Generates a password-protected Private Key and a Public Key.
    Sets secure file permissions on the private key.
    """
    password = getpass.getpass("Set a password for the new Private Key (min 12 chars): ").encode()
    
    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"❌ Error: Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        write_log("GENKEY", "N/A", "FAILED", "Password too short")
        return
    
    # Check password strength
    if password.isdigit() or password.isalpha():
        print("⚠️  Warning: Consider using a mix of letters, numbers, and symbols for stronger security.")
    
    try:
        # Generate RSA key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        # Save private key with encryption
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(password)
            ))
        
        # Set secure permissions (owner read/write only)
        os.chmod(PRIVATE_KEY_FILE, 0o600)
        
        # Save public key
        public_key = private_key.public_key()
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print("\n✅ Keys generated successfully.")
        print(f"   Private key: {PRIVATE_KEY_FILE} (permissions: 600)")
        print(f"   Public key:  {PUBLIC_KEY_FILE}")
        print("\n⚠️  IMPORTANT: Keep your private key and password secure!")
        write_log("GENKEY", "N/A", "SUCCESS", "Keys created with secure permissions")
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        write_log("GENKEY", "N/A", "FAILED", str(e))


# --- Core Logic ---
def get_file_hash(filepath: str) -> Optional[str]:
    """
    Calculate SHA-256 hash of a file using streaming for memory efficiency.
    
    Args:
        filepath: Path to the file to hash
        
    Returns:
        Hexadecimal hash string, or None if file not found
    """
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None
    except Exception:
        return None


def sign_file(filepath: str, name: str, github: Optional[str] = None) -> None:
    """
    Sign a file with RSA digital signature.
    
    Args:
        filepath: Path to the file to sign
        name: Name of the signer
        github: Optional GitHub profile URL
    """
    if not os.path.exists(PRIVATE_KEY_FILE):
        print(f"❌ Error: {PRIVATE_KEY_FILE} not found. Run 'signas genkey' first.")
        write_log("SIGN", filepath, "FAILED", "Private key not found")
        return

    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found.")
        write_log("SIGN", filepath, "FAILED", "Target file not found")
        return

    password = getpass.getpass("Enter Private Key password: ").encode()

    try:
        # Load private key
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=password)

        # Calculate file hash
        file_hash = get_file_hash(filepath)
        if not file_hash:
            raise FileNotFoundError(f"Cannot read file: {filepath}")

        # Prepare signature info
        sign_info = {"hash": file_hash, "signer": name}
        if github:
            sign_info["github"] = github
        
        # Create digital signature
        json_data = json.dumps(sign_info, sort_keys=True).encode()
        signature = private_key.sign(
            json_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        # Save signature file
        final_output = {
            "info": sign_info,
            "signature": base64.b64encode(signature).decode('utf-8')
        }
        
        signature_path = filepath + ".signas"
        with open(signature_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Signature created: {signature_path}")
        print(f"   File hash: {file_hash}")
        print(f"   Signer: {name}")
        if github:
            print(f"   GitHub: {github}")
        write_log("SIGN", filepath, "SUCCESS", f"Signed by {name}")
        
    except ValueError as e:
        print(f"\n❌ Error: Incorrect password or corrupted private key.")
        write_log("SIGN", filepath, "FAILED", "Authentication failed")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        write_log("SIGN", filepath, "FAILED", str(e))
    except Exception as e:
        print(f"\n❌ Error: {e}")
        write_log("SIGN", filepath, "FAILED", str(e))


def verify_file(filepath: str) -> None:
    """
    Verify file signature and integrity.
    
    Args:
        filepath: Path to the file to verify
    """
    sign_path = filepath + ".signas"
    
    # Check required files
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found.")
        write_log("VERIFY", filepath, "FAILED", "File not found")
        return
        
    if not os.path.exists(sign_path):
        print(f"❌ Error: Signature file '{sign_path}' not found.")
        write_log("VERIFY", filepath, "FAILED", "Signature file missing")
        return
        
    if not os.path.exists(PUBLIC_KEY_FILE):
        print(f"❌ Error: {PUBLIC_KEY_FILE} not found.")
        write_log("VERIFY", filepath, "FAILED", "Public key missing")
        return

    try:
        # Load public key
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        
        # Load signature data
        with open(sign_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Verify signature
        sign_info_bytes = json.dumps(data["info"], sort_keys=True).encode()
        signature = base64.b64decode(data["signature"])

        public_key.verify(
            signature,
            sign_info_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        # Verify file hash
        current_hash = get_file_hash(filepath)
        if current_hash == data["info"]["hash"]:
            print("✅ Verification Successful.")
            print(f"   Signer: {data['info']['signer']}")
            if "github" in data["info"]:
                print(f"   GitHub: {data['info']['github']}")
            print(f"   File hash: {current_hash}")
            write_log("VERIFY", filepath, "SUCCESS", f"Authentic (signed by {data['info']['signer']})")
        else:
            print("❌ Verification Failed: File content has been tampered with!")
            print(f"   Expected hash: {data['info']['hash']}")
            print(f"   Actual hash:   {current_hash}")
            write_log("VERIFY", filepath, "FAILED", "File hash mismatch")
            
    except InvalidSignature:
        print("❌ Verification Failed: Invalid or forged signature.")
        write_log("VERIFY", filepath, "FAILED", "Invalid signature")
    except json.JSONDecodeError:
        print("❌ Error: Corrupted signature file.")
        write_log("VERIFY", filepath, "FAILED", "Corrupted signature file")
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        write_log("VERIFY", filepath, "FAILED", str(e))


def hash_file(filepath: str) -> None:
    """
    Display SHA-256 hash of a file without signing.
    
    Args:
        filepath: Path to the file to hash
    """
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found.")
        write_log("HASH", filepath, "FAILED", "File not found")
        return
        
    file_hash = get_file_hash(filepath)
    if file_hash:
        print(f"SHA-256: {file_hash}")
        print(f"File: {filepath}")
        write_log("HASH", filepath, "SUCCESS", f"Hash: {file_hash}")
    else:
        print(f"❌ Error: Could not calculate hash for '{filepath}'")
        write_log("HASH", filepath, "FAILED", "Hash calculation failed")


def print_usage() -> None:
    """Print usage information."""
    print("""
Signas - File Digital Signature Tool

Usage:
  signas genkey                          Generate new key pair
  signas sign <file> <name> [github]     Sign a file
  signas verify <file>                   Verify a file signature
  signas hash <file>                     Calculate file hash

Examples:
  signas genkey
  signas sign document.pdf "John Doe" "https://github.com/johndoe"
  signas verify document.pdf
  signas hash document.pdf
    """)


def main() -> None:
    """Main CLI entry point."""
    args = sys.argv
    
    if len(args) < 2:
        print_usage()
        return

    cmd = args[1].lower()
    
    if cmd == "genkey":
        generate_keys()
    elif cmd == "sign" and len(args) >= 4:
        github = args[4] if len(args) > 4 else None
        sign_file(args[2], args[3], github)
    elif cmd == "verify" and len(args) >= 3:
        verify_file(args[2])
    elif cmd == "hash" and len(args) >= 3:
        hash_file(args[2])
    else:
        print("❌ Invalid command.")
        print_usage()


if __name__ == "__main__":
    main()
