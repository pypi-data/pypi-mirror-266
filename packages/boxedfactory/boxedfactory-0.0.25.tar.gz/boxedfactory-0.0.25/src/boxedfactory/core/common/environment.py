import os

def getenv(name:str, default_value:None):
    return os.environ.get(name, default_value)