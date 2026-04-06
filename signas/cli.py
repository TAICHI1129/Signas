import hashlib
import sys
import os
import json

def file_to_hex(filepath):
    """ファイルを読み込んで16進数の文字列に変換"""
    with open(filepath, "rb") as f:
        data = f.read()
    return data.hex()

def hash_hex(hex_string):
    """16進数文字列のSHA-256ハッシュを計算"""
    h = hashlib.sha256()
    h.update(hex_string.encode())
    return h.hexdigest()

def sign_file(filepath, name, github=None):
    """署名ファイル (.signas) を作成"""
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

def verify_file(filepath):
    """ファイルと .signas を照合して検証"""
    sign_path = filepath + ".signas"
    if not os.path.exists(sign_path):
        print(f"Error: Signature file '{sign_path}' not found.")
        return

    # 現在のファイルのハッシュを計算
    current_hex = file_to_hex(filepath)
    current_hash = hash_hex(current_hex)

    # 署名ファイルの情報を読み込み
    with open(sign_path, "r") as f:
        sign_data = json.load(f)
    
    saved_hash = sign_data.get("hash")

    if current_hash == saved_hash:
        print("✅ Verification Successful: File is intact.")
        print(f"Signed by: {sign_data.get('signer')}")
    else:
        print("❌ Verification Failed: File has been modified!")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python script.py sign <file> <name> [github_url]")
        print("  python script.py verify <file>")
        print("  python script.py view_info <signas_file>")
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

    elif cmd == "verify":
        if len(sys.argv) < 3:
            print("Error: Filepath is required")
            return
        verify_file(sys.argv[2])

    elif cmd == "view_info":
        if len(sys.argv) < 3:
            print("Error: .signas filepath is required")
            return
        sign_path = sys.argv[2]
        try:
            with open(sign_path, "r") as f:
                data = json.load(f)
                print(f"Signer: {data.get('signer')}")
                print(f"Hash:   {data.get('hash')}")
                if "github" in data:
                    print(f"GitHub: {data.get('github')}")
        except FileNotFoundError:
            print("Error: Signature file not found")
        except json.JSONDecodeError:
            print("Error: Failed to decode signature file")

    elif cmd == "hash":
        if len(sys.argv) < 3:
            print("Error: Filepath is required")
            return
        print(hash_hex(file_to_hex(sys.argv[2])))

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
