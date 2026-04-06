# Signas

Secure File Digital Signature & Integrity Verification Tool

Signas is a lightweight digital signature tool built in Python.
It uses RSA (2048-bit) asymmetric cryptography to ensure not only file integrity but also the authenticity of the signer.

---

## 🔗 Developer API Documentation

For programmatic usage, see:
https://github.com/TAICHI1129/Signas/blob/main/api.md

---

## Features

* **RSA Digital Signatures**
  Prevents forgery of signature files (`.signas`).

* **Strong Tamper Detection**
  Uses SHA-256 with streaming to verify even multi-GB files with low memory usage.

* **Identity Verification**
  Includes signer name and optional GitHub profile.

* **Audit Log**
  All signing and verification activities are automatically recorded in `audit.log`.

* **Password Protection**
  Private keys are encrypted with a passphrase to prevent misuse if stolen.

---

## Installation

```bash
pip install signas
```

> Note: Requires the `cryptography` library for RSA functionality.

---

## CLI Usage

### 1. Generate Key Pair

Before signing, generate your personal key pair:

```bash
signas genkey
```

* `private_key.pem` → **Keep this secret**
* `public_key.pem` → Share with others for verification

---

### 2. Sign a File

Create a signature file to prove authenticity:

```bash
signas sign <file> <signer_name> [github_url]
```

Example:

```bash
signas sign data.zip TAICHI1129 https://github.com
```

---

### 3. Verify a File

Verify integrity and authenticity:

```bash
signas verify <file>
```

Requirements:

* Target file
* `<file>.signas`
* `public_key.pem`

---

## .signas File Format

`.signas` is a JSON file containing:

* `info`

  * SHA-256 hash
  * signer name
  * GitHub link (optional)
* `signature`

  * Base64-encoded RSA-PSS signature

### Example

```json
{
  "info": {
    "hash": "5a51be41913d0...",
    "signer": "TAICHI1129",
    "github": "https://github.com"
  },
  "signature": "MIIBIjANBgkqh..."
}
```

---

## Security Notes

* **Private Key Management**
  Losing `private_key.pem` or its password means you can no longer sign files.

* **Public Key Distribution**
  Always obtain public keys from trusted sources.

---

## Usage Examples

### 1. Generate Keys (One-time setup)

```bash
signas genkey
```

Input:

* Password to protect your private key

Output:

* `private_key.pem`
* `public_key.pem`

---

### 2. Sign a File

#### Example A (Name only)

```bash
signas sign report.pdf "Taro Yamada"
```

#### Example B (With GitHub link)

```bash
signas sign software.zip "TAICHI1129" "https://github.com"
```

Input:

* Password set during key generation

Output:

* `report.pdf.signas` or `software.zip.signas`

---

### 3. Verify a File

Run in a directory containing:

* target file
* `.signas` file
* `public_key.pem`

```bash
signas verify software.zip
```

#### Success

```
✅ Verification Successful
```

#### Failure (Tampered)

```
❌ Verification Failed: File content has been tampered with!
```

#### Failure (Invalid Signature)

```
❌ Verification Failed: Invalid or forged signature.
```

---

### 4. View Audit Log

```bash
# Windows
type audit.log

# Mac / Linux
cat audit.log
```

Example:

```
[2024-05-20 12:00:00] ACTION: SIGN | FILE: software.zip | STATUS: SUCCESS | Signed by TAICHI1129
```

---

### 5. Hash Only

```bash
signas hash sample.txt
```

---

## Windows Users

If the `signas` command does not work:

```bash
python -m signas.cli
```

---

## Summary

Signas provides:

* Secure digital signatures (RSA)
* Reliable tamper detection (SHA-256)
* CLI and JSON API support

Use CLI for manual operations and the JSON API for development.
