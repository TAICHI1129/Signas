import hashlib
import sys
import os
import json

def file_to_hex(filepath):
    """Convert file bytes to hex string (no separator)."""
    with open(filepath, "rb") as f:
        data = f.read()
    return data.hex()

def hash_hex(hex_string):
    """Compute SHA-256 hash of hex string."""
    h = hashlib.sha256()
    h.update(hex_string.encode())
    return h.hexdigest()

def sign_file(filepath, name, github=None):
    """Create .signas file with hash, signer name, and optional GitHub link."""
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' does not exist")
        return

    hex_str = file_to_hex(filepath)
    hashed = hash_hex(hex_str)

    sign_data = {
        "hash": hashed,
        "signer": name
    }
    if github:
        sign_data["github"] = github

    sign_path = filepath + ".signas"
    with open(sign_path, "w") as f:
        json.dump(sign_data, f, indent=2)
    
    print(f"Signature created: {sign_path}")

def usage():
    print("Signas CLI")
    print("Usage:")
    print("  signas sign <file> <name> [github] : Sign the file with name and optional GitHub")
    print("  signas hash <file>                  : Show SHA-256 hash of the file")

def main():
    if len(sys.argv) < 3:
        usage()
        return

    cmd = sys.argv[1].lower()
    if cmd == "sign":
        if len(sys.argv) < 4:
            print("Error: Signer name is required")
            return
        filepath = sys.argv[2]
        name = sys.argv[3]
        github = sys.argv[4] if len(sys.argv) > 4 else None
        sign_file(filepath, name, github)
    elif cmd == "hash":
        filepath = sys.argv[2]
        hex_str = file_to_hex(filepath)
        hashed = hash_hex(hex_str)
        print(hashed)
    else:
        usage()

if __name__ == "__main__":
    main()
