import os
import json
import base64
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend


def get_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_keys(password: bytes):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    encrypted_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    )

    with open("private_key.pem", "wb") as f:
        f.write(encrypted_private)

    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open("public_key.pem", "wb") as f:
        f.write(public_bytes)

    return {
        "status": "success",
        "private_key": "private_key.pem",
        "public_key": "public_key.pem"
    }


def sign_file(file_path, signer, password: bytes, github=None):
    file_hash = get_file_hash(file_path)

    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=password
        )

    info = {
        "hash": file_hash,
        "signer": signer,
        "github": github
    }

    info_bytes = json.dumps(info).encode()

    signature = private_key.sign(
        info_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    output = {
        "info": info,
        "signature": base64.b64encode(signature).decode()
    }

    out_file = file_path + ".signas"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    return {
        "status": "success",
        "file": file_path,
        "signer": signer,
        "hash": file_hash,
        "output": out_file
    }


def verify_file(file_path):
    with open(file_path + ".signas", "r") as f:
        data = json.load(f)

    info = data["info"]
    signature = base64.b64decode(data["signature"])

    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    try:
        public_key.verify(
            signature,
            json.dumps(info).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        return {"status": "error", "reason": "invalid_signature"}

    current_hash = get_file_hash(file_path)

    if current_hash != info["hash"]:
        return {"status": "error", "reason": "tampered"}

    return {
        "status": "success",
        "file": file_path,
        "signer": info["signer"],
        "hash": info["hash"],
        "github": info.get("github")
    }


def hash_file(file_path):
    return {
        "status": "success",
        "file": file_path,
        "hash": get_file_hash(file_path)
    }
