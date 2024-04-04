from typing import Union
import json

Obj = dict[str, Union['Obj', str]]

class ConfigurationBehaviour:
    def __init__(
            self,
            always_reload:bool = False,
            raise_exception_on_not_found:bool = False
            ) -> None:
        self.always_reload = always_reload
        self.raise_exception_on_not_found = raise_exception_on_not_found

class Configuration:
    def __init__(self, location:str, behaviour:ConfigurationBehaviour = None) -> None:
        self.location = location
        self.behaviour:ConfigurationBehaviour = behaviour or ConfigurationBehaviour()
        self.root = {}
        self.load()

    def load(self):
        try:
            with open(self.location, 'r') as fi:
                self.root = json.load(fi)
        except Exception as e:
            print(e)

    def get_value(self, path:str, node:dict[str, str] = None, default_value = None, path_description:str = None) -> Obj:
        path_description = path_description or path
        if node == None:
            if self.behaviour.always_reload:
                self.load()
            return self.get_value(path, self.root, default_value, path_description)
        if isinstance(node, dict):
            current, *rest = path.split(":")
            if current in node:
                if len(rest) > 0:
                    return self.get_value(":".join(rest), node[current], default_value, path_description)
                else:
                    return node[current]
        if self.behaviour.raise_exception_on_not_found:
            raise Exception(f"Missing configuration: {path_description}") 
        else:
            return default_value
    
class Configurable:
    def __init__(self, config:Configuration) -> None:
        self.config:Configuration = config