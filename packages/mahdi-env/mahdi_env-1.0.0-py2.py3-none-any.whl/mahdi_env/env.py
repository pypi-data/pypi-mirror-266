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
    """ This calss is a subclass of dict that returns a default value of
    empty string when the key is not present, this is useful when the ENV
    is not defined so the programm doesn't crash.
    """

    def __getitem__(self , key , default = '') :
        return super().__getitem__(key) if key in self else default

def get_env() -> ENVDict :
    """ Reads the environment variables from the .export file and returns them """
    if 'DB' in environ :
        return ENVDict(environ)

    fn = Path(f"{environ['HOME']}/.export")
    if not fn.exists() :
        fn = Path(f"/homes/nber/mahdimir/.export")

    with open(fn) as f :
        script = f.read()
    script = script.encode() + b'\nenv'

    with subprocess.Popen(['sh'] ,
                          stdin = subprocess.PIPE ,
                          stdout = subprocess.PIPE) as p :
        result = p.communicate(script)

    for line in result[0].decode().splitlines() :
        var , _ , value = line.partition('=')
        environ[var] = value

    if not 'DB' in environ :
        raise Exception('DB is not set in environment variables.')

    return ENVDict(environ)
