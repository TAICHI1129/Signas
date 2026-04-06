import hashlib
import sys
import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# --- 鍵の管理機能 ---
def generate_keys():
    """秘密鍵と公開鍵のペアを生成して保存"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print("✅ Keys generated: private_key.pem, public_key.pem")

# --- ファイル処理 ---
def get_file_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def sign_file(filepath, name, github=None):
    """秘密鍵を使ってデジタル署名を作成"""
    if not os.path.exists("private_key.pem"):
        print("Error: private_key.pem not found. Run 'genkey' first.")
        return

    # 1. 秘密鍵の読み込み
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # 2. ハッシュとデータの準備
    file_hash = get_file_hash(filepath)
    sign_info = {"hash": file_hash, "signer": name}
    if github: sign_info["github"] = github
    
    json_data = json.dumps(sign_info, sort_keys=True).encode()

    # 3. デジタル署名（RSA）の作成
    signature = private_key.sign(
        json_data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    # 4. 保存
    final_output = {
        "info": sign_info,
        "signature": base64.b64encode(signature).decode('utf-8')
    }
    
    with open(filepath + ".signas", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Digital Signature created: {filepath}.signas")

def verify_file(filepath):
    """公開鍵を使ってデジタル署名を検証"""
    sign_path = filepath + ".signas"
    if not os.path.exists(sign_path) or not os.path.exists("public_key.pem"):
        print("Error: .signas file or public_key.pem missing.")
        return

    # 1. 公開鍵と署名データの読み込み
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    with open(sign_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    sign_info_bytes = json.dumps(data["info"], sort_keys=True).encode()
    signature = base64.b64decode(data["signature"])

    # 2. RSA署名の検証
    try:
        public_key.verify(
            signature,
            sign_info_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        # 3. ファイル本体のハッシュ検証
        current_hash = get_file_hash(filepath)
        if current_hash == data["info"]["hash"]:
            print("✅ Verified: The signature is authentic and the file is intact.")
            print(f"Signed by: {data['info']['signer']}")
            if "github" in data["info"]: print(f"GitHub: {data['info']['github']}")
        else:
            print("❌ Failed: The file content has been tampered with!")
    except Exception:
        print("❌ Failed: The signature itself is invalid or forged!")

# --- メイン処理 ---
def main():
    if len(sys.argv) < 2:
        print("Usage:\n  python script.py genkey\n  python script.py sign <file> <name> [github]\n  python script.py verify <file>")
        return

    cmd = sys.argv[1].lower()
    if cmd == "genkey":
        generate_keys()
    elif cmd == "sign" and len(sys.argv) >= 4:
        sign_file(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "verify" and len(sys.argv) >= 3:
        verify_file(sys.argv[2])
    else:
        print("Invalid command or arguments.")

if __name__ == "__main__":
    main()
