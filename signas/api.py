import io
from contextlib import redirect_stdout, redirect_stderr
from signas import cli


def _capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        try:
            func(*args, **kwargs)
        except SystemExit:
            # argparse系がexitする対策
            pass
    return buf.getvalue()


def generate_key():
    return _capture_output(cli.generate_keys)


def sign(file, signer, github=None):
    return _capture_output(cli.sign_file, file, signer, github)


def verify(file):
    return _capture_output(cli.verify_file, file)


def hash(file):
    return _capture_output(cli.hash_file, file)
