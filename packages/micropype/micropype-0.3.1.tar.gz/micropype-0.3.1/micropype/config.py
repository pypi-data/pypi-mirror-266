from typing import List
import json
from micropype.utils import MessageIntent, cprint, merge_dicts


def read_annotations(cls):
    """ 
        Parameters
        ==========
    
    """
    attributes = {}
    for attr, attr_type in cls.__annotations__.items():
        default = cls.__getattribute__(cls, attr) if hasattr(cls, attr) else None

        # If the attribute is optional, get it's subtype
        attr_type = attr_type.__args__[0] if attr_type.__name__ == "Optional" else attr_type

        t = attr_type.__name__

        sub_t = None
        if hasattr(attr_type, "__name__") and attr_type.__name__ == "List":
            if len(attr_type.__args__) > 0:
                sub_t = attr_type.__args__[0].__name__
            t = list
                
    
        attributes[attr] = (t, default, sub_t)
    return attributes


class Config:
    _children = {}

    def __init__(self, json_f=None, priority="file", **kwargs) -> None:
        """
            Parameters
            ==========
            json_f: str
            priority: "json" or "kwargs"
                Which config values to use even if defined in the other method.
        """
        if json_f is not None:
            ycfg = json.load(open(json_f, 'r'))
            if priority == "file":
                kwargs = merge_dicts(kwargs, ycfg)
            elif priority == "kwargs":
                kwargs = merge_dicts(ycfg, kwargs)
            else:
                raise ValueError("")

        attributes = read_annotations(self.__class__)

        #
        used_kwargs = 0 
        for attr_name, (attr_t, default_v, sub_type) in attributes.items():
            useDefault = not attr_name in kwargs
            if not useDefault:
                used_kwargs += 1

            if attr_t in self._children or (attr_t in [list, tuple] and sub_type in self._children):
                if useDefault:
                    value = [] if attr_t in [list, tuple] else self._children[attr_t]
                # If it is a sub Config
                elif type(kwargs[attr_name]).__name__ == "dict":
                    value = self._children[attr_t](**kwargs[attr_name])
                # If it is a list of Config
                elif attr_t in [list, tuple] and len(kwargs[attr_name]) > 0 and type(kwargs[attr_name][0]).__name__ == "dict":
                    value = list(self._children[sub_type](**kwargs[attr_name][i]) for i in range(len(kwargs[attr_name])))
                else:
                    value = kwargs[attr_name]
            else:
                value = default_v if useDefault else kwargs[attr_name]
            self.__setattr__(attr_name, value)

        # Print a message if a argument was passed but not used as it is no part
        # of this config object
        if used_kwargs < len(kwargs.keys()):
            for k in kwargs.keys():
                if not k in attributes.keys():
                    cprint(
                        f'"{k}" is not an attribute of {self.__class__.__name__}. Skipping this setting.',
                        intent=MessageIntent.WARNING
                    )
                    continue

    @classmethod
    def register(cls, child_class):
        cls._children[child_class.__name__] = child_class
        return child_class
    

    def to_dict(self) -> dict:
        result = {}
        for name, value in self.__dict__.items():
            if isinstance(value, Config):
                result[name] = value.to_dict()
            elif isinstance(value, list):
                result[name] = [item.to_dict() if isinstance(item, Config) else item for item in value]
            elif isinstance(value, dict):
                result[name] = {key: value.to_dict() if isinstance(value, Config) else value for key, value in value.items()}
            else:
                result[name] = value
        return result

    def to_json(self, filepath:str):
        with open(filepath, 'w') as fp:
            json.dump(self.to_dict(), fp, indent=4)

    def keys(self) -> List[str]:
        return list(filter(lambda k: not k.startswith('_'), self.__dict__.keys()))
    
    def __getitem__(self, name: str):
        if hasattr(self, name):
            return getattr(self, name)
        raise ValueError(f'This config has no {name} attribute.')
