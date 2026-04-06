import io
import sys
from contextlib import redirect_stdout
from signas import cli

def _capture_output(func, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()

def sign(file, name, github=None, password=None):
    return _capture_output(cli.sign_file, file, name, github, password)
