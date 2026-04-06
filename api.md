# Signas Developer API Documentation

## Overview

Signas provides a programmatic API for secure digital signing and verification of files using RSA (2048-bit) and SHA-256.

The API is designed to be:

* CLI-compatible (legacy functions)
* JSON-based (recommended for developers)

---

## Installation

```bash
pip install signas
```

---

## Import

```python
import signas
```

---

# JSON API (Recommended)

These functions return structured Python dictionaries and are intended for programmatic use.

---

## 1. Generate Key Pair

```python
signas.generate_key_json(password: str) -> dict
```

### Description

Generates an RSA key pair and saves them as:

* `private_key.pem`
* `public_key.pem`

### Example

```python
result = signas.generate_key_json("strongpassword123")
```

### Returns

```python
{
  "status": "success",
  "private_key": "private_key.pem",
  "public_key": "public_key.pem"
}
```

---

## 2. Hash File

```python
signas.hash_json(file: str) -> dict
```

### Description

Calculates SHA-256 hash of a file.

### Example

```python
result = signas.hash_json("sample.txt")
```

### Returns

```python
{
  "status": "success",
  "file": "sample.txt",
  "hash": "..."
}
```

---

## 3. Sign File

```python
signas.sign_json(file: str, signer: str, password: str, github: str | None = None) -> dict
```

### Description

Creates a digital signature file (`.signas`) for the specified file.

### Example

```python
result = signas.sign_json("data.zip", "TAICHI1129", "strongpassword123")
```

### Returns

```python
{
  "status": "success",
  "file": "data.zip",
  "signer": "TAICHI1129",
  "hash": "...",
  "output": "data.zip.signas"
}
```

---

## 4. Verify File

```python
signas.verify_json(file: str) -> dict
```

### Description

Verifies file integrity and signature authenticity.

### Example

```python
result = signas.verify_json("data.zip")
```

### Returns (Success)

```python
{
  "status": "success",
  "file": "data.zip",
  "signer": "TAICHI1129",
  "hash": "...",
  "github": "https://github.com"  # or None
}
```

### Returns (Failure)

```python
{
  "status": "error",
  "reason": "tampered"
}
```

or

```python
{
  "status": "error",
  "reason": "invalid_signature"
}
```

---

# Legacy CLI-Compatible API

These functions mimic CLI behavior and return raw output strings.

⚠️ Not recommended for programmatic use.

```python
signas.generate_key()
signas.sign(file, signer, github=None)
signas.verify(file)
signas.hash(file)
```

---

# Error Handling

All JSON API functions follow this pattern:

```python
{
  "status": "success" | "error",
  ...
}
```

### Recommended usage

```python
result = signas.verify_json("file.txt")

if result["status"] == "success":
    print("Valid file")
else:
    print("Error:", result["reason"])
```

---

# File Requirements

For verification:

* `<file>`
* `<file>.signas`
* `public_key.pem`

must exist in the same directory.

---

# Security Notes

* Never share `private_key.pem`
* Always protect private key with a strong password
* Distribute `public_key.pem` through trusted channels

---

# Design Notes

* JSON API is powered by `core.py` (no CLI dependency)
* CLI compatibility is preserved for backward support
* Future versions may deprecate raw-output API

---

# Summary

| Feature          | CLI API | JSON API |
| ---------------- | ------- | -------- |
| Human-readable   | ✅       | ❌        |
| Machine-readable | ❌       | ✅        |
| Recommended      | ❌       | ✅        |

---

Use JSON API for all development purposes.
