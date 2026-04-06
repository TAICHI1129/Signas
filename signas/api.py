from signas import cli

def generate_key(password: str):
    return cli.generate_keys(password)

def sign(file, name, github=None, password=None):
    return cli.sign_file(file, name, github, password)

def verify(file):
    return cli.verify_file(file)

def hash(file):
    return cli.hash_file(file)
