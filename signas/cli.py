import hashlib
import sys
import os
import json
import base64
import getpass
from datetime import datetime # 日時記録用
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# --- Logging function ---
def write_log(action, filepath, status, details=""):
    """Records actions to audit.log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ACTION: {action} | FILE: {filepath} | STATUS: {status} | {details}\n"
    with open("audit.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

# --- Key Management ---
def generate_keys():
    """Generates a password-protected Private Key and a Public Key."""
    password = getpass.getpass("Set a password for the new Private Key: ").encode()
    if len(password) < 4:
        print("Error: Password is too short (min 4 characters).")
        return
    
    try:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open("private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(password)
            ))
        
        public_key = private_key.public_key()
        with open("public_key.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("\n✅ Keys generated successfully.")
        write_log("GENKEY", "N/A", "SUCCESS", "Keys created")
    except Exception as e:
        print(f"Error: {e}")
        write_log("GENKEY", "N/A", "FAILED", str(e))

# --- Core Logic ---
def get_file_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

def sign_file(filepath, name, github=None):
    if not os.path.exists("private_key.pem"):
        print("Error: private_key.pem not found.")
        return

    password = getpass.getpass("Enter Private Key password: ").encode()

    try:
        with open("private_key.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=password)

        file_hash = get_file_hash(filepath)
        if not file_hash:
            raise FileNotFoundError(f"File {filepath} not found.")

        sign_info = {"hash": file_hash, "signer": name}
        if github: sign_info["github"] = github
        
        json_data = json.dumps(sign_info, sort_keys=True).encode()
        signature = private_key.sign(
            json_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        final_output = {
            "info": sign_info,
            "signature": base64.b64encode(signature).decode('utf-8')
        }
        
        with open(filepath + ".signas", "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Signature created: {filepath}.signas")
        write_log("SIGN", filepath, "SUCCESS", f"Signed by {name}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        write_log("SIGN", filepath, "FAILED", str(e))

def verify_file(filepath):
    sign_path = filepath + ".signas"
    if not os.path.exists(sign_path) or not os.path.exists("public_key.pem"):
        print("Error: Missing signature file or public key.")
        write_log("VERIFY", filepath, "FAILED", "Missing files")
        return

    try:
        with open("public_key.pem", "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        
        with open(sign_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        sign_info_bytes = json.dumps(data["info"], sort_keys=True).encode()
        signature = base64.b64decode(data["signature"])

        public_key.verify(
            signature,
            sign_info_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        current_hash = get_file_hash(filepath)
        if current_hash == data["info"]["hash"]:
            print("✅ Verification Successful.")
            write_log("VERIFY", filepath, "SUCCESS", "Authentic")
        else:
            print("❌ Verification Failed: Tampered.")
            write_log("VERIFY", filepath, "FAILED", "Tampered file content")
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        write_log("VERIFY", filepath, "FAILED", "Invalid signature/forged")

def main():
    args = sys.argv
    if len(args) < 2:
        print("Usage:\n  python script.py genkey\n  python script.py sign <file> <name> [github]\n  python script.py verify <file>")
        return

    cmd = args[1].lower()
    if cmd == "genkey":
        generate_keys()
    elif cmd == "sign" and len(args) >= 4:
        sign_file(args[2], args[3], args[4] if len(args) > 4 else None)
    elif cmd == "verify" and len(args) >= 3:
        verify_file(args[2])
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
