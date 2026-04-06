from signas import cli
from signas import core
import io
from contextlib import redirect_stdout, redirect_stderr


def _capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        try:
            func(*args, **kwargs)
        except SystemExit:
            pass
    return buf.getvalue()


# ===== JSON API（NEW） =====

def generate_key_json(password: str):
    return core.generate_keys(password.encode())


def sign_json(file, signer, password: str, github=None):
    return core.sign_file(file, signer, password.encode(), github)


def verify_json(file):
    return core.verify_file(file)


def hash_json(file):
    return core.hash_file(file)


# ===== 既存互換（CLIラップ） =====

def generate_key():
    return _capture_output(cli.generate_keys)


def sign(file, signer, github=None):
    return _capture_output(cli.sign_file, file, signer, github)


def verify(file):
    return _capture_output(cli.verify_file, file)


def hash(file):
    return _capture_output(cli.hash_file, file)
