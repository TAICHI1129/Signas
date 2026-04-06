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

def main():
    if len(sys.argv) < 2: # 引数が足りない場合のチェック
        print("Usage: python script.py [sign|hash|view_info] [file] [name] [github]")
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
        if len(sys.argv) < 3:
            print("Error: Filepath is required")
            return
        filepath = sys.argv[2]
        hex_str = file_to_hex(filepath)
        hashed = hash_hex(hex_str)
        print(hashed)

    elif cmd == "view_info":
        if len(sys.argv) < 3:
            print("Error: .signas filepath is required")
            return
        sign_path = sys.argv[2]
        try:
            with open(sign_path, "r") as f:
                sign_data = json.load(f)
                print(f"Signer: {sign_data.get('signer')}")
                print(f"Hash:   {sign_data.get('hash')}")
        except FileNotFoundError:
            print("Error: Signature file not found")

    else:
        print("Command not found")

if __name__ == "__main__":
    main()
