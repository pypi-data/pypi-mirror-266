"""

    Loads the environment variables from the .export file if
        - The DB environment variable is not set that means either:
            - I am running in the console
            - or other user than me is running the script.

    """

import subprocess
from os import environ
from pathlib import Path

class ENVDict(dict) :
    """

    This calss is a subclass of dict that returns a default value of
    empty string when the key is not present.
    This is useful when the ENV is not defined so the programm doesn't crash.
    like when there is no access to the .export file. (like another user is running the script)
    or when some environment variables are not set in the current machine but are set in another machine. (like Genomics server) but not on the local machine.

    """

    def __getitem__(self , key , default = '') :
        return super().__getitem__(key) if key in self else default

def get_env() -> ENVDict :
    """

    Reads the environment variables from the .export file and returns them

    """

    fn = Path(f"{environ['HOME']}/.export")
    if not fn.exists() :
        fn = Path('/homes/nber/mahdimir/.export')

    if not fn.exists() :
        return ENVDict(environ)

    with open(fn) as f :
        script = f.read()

    script = script.encode() + b'\nenv'

    _sp = subprocess.PIPE
    with subprocess.Popen(['sh'] , stdin = _sp , stdout = _sp) as p :
        result = p.communicate(script)

    for line in result[0].decode().splitlines() :
        var , _ , value = line.partition('=')
        environ[var] = value

    return ENVDict(environ)
