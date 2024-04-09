from typing import Any, List, get_type_hints
import importlib
import inspect

from micropype.utils import auto_cast
from . import Config


def parse_args(args: str) -> dict:
    """ Convert
        --arg1 val1 --arg2 --arg3 val3.1 val3.2 --arg4 
        in
        {"arg1": val1, "arg2": True, "arg3", [val3.1, val3.2], "arg4": True}
    """
    pos_args = []
    kwargs = {}
    a = 0
    while a < len(args):
        arg = args[a]
        if arg.startswith("--"):
            key = arg[2:]
            # This keyword args value
            for a2 in range(a+1, len(args)):
                if args[a2].startswith("--"):
                    a2 -= 1
                    break
            if a2 == a+1:
                kwargs[key] = auto_cast(args[a+1])
            elif a2 > a+1:
                kwargs[key] = list(auto_cast(val) for val in args[a+1: a2+1])
            else:
                kwargs[key] = True
            a = a2 + 1
        else:
            # This is still positional args
            pos_args.append(auto_cast(arg))     
            a += 1  
    return pos_args, kwargs


def get_all_type_hints(obj) -> dict:
    """ Return all attribute as keys and annotation type as values. """
    all_hints = {}
    for base_cls in type(obj).__mro__:
        all_hints.update(get_type_hints(base_cls))
    return all_hints


def init_class_attribute(obj, attribut_name):
    """ Create a new instance of an object by calling the contrustor without any args. """
    if hasattr(obj, attribut_name):
        obj.__setattr__(attribut_name, get_all_type_hints(obj)[attribut_name]())
        return obj
    raise KeyError(f'Object {type(obj)} has no attribute "{attribut_name}".')


def override_config_with_arg(config: Config, arg_path:List[str], value:Any):
    """ Overwrite config property base on the splitted argument path. """
    if len(arg_path) == 0:
        raise ValueError(f'No path.')
    attr = arg_path[0]
    if not attr in get_all_type_hints(config):
        raise ValueError(f'Invalid path "{".".join(arg_path)}" for config "{type(config).__name__}".')
    
    # attr_type = type(config.__getattribute__(attr))
    if len(arg_path) > 1:
        val = config.__getattribute__(attr)
        if val is None or type(val).__name__ == "type":
            config = init_class_attribute(config, attr)
        val = override_config_with_arg(config.__getattribute__(attr), arg_path[1:], value)
    else:
        val = value
    
    config.__setattr__(arg_path[0], val)
    return config


def override_config_with_args(config: Config, parsed_args: dict):
    """ Overwrite all the request args. """
    for path, val in parsed_args.items():
        splt = path.split(".")
        config = override_config_with_arg(config, splt, val)
    return config


def import_function_by_path(function_path: str):
    """ Dynamic python import of an object of a python module. """
    module_path, function_name = function_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)


def list_function_arguments(func) -> dict:
    """ Return the list of function arguments. """
    signature = inspect.signature(func)
    parameters = signature.parameters
    arguments_info = {}
    for param_name, param in parameters.items():
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
        arguments_info[param_name] = param_type
    return arguments_info


def run_function_from_commandline(function_path: str, *args):
    """ Run a Python function using arguments of a command line.

        First, the function is imported and the arguments that match function definition are found,
        they are use when running the function as kwargs.

        If a "--config path/to/config/file.json" is in args and that the function definition
        uses a config parameter of type micropype.Config (or subclass), the config file is loaded
        to initialze the config.

        If some arguments are not used in the function definition, they are used to override the
        load config.

        If the first argument points to a non-callable object, the object is returned.

        Parameters
        ==========
        function_path: str
            The pythonic path to the function to be executed (ex: module.submodule.function_name)
        *args: List[str]
            A list of commandline inputs. 
            For example, with: $python script.py module.funcname --arg1 val1,
            use run_function_from_commandline(sys.argv[1:])

        Return
        ======
        It return the function result or the value of the path if not callable.    
    """
    # Import the function and get the list of arguments
    function = import_function_by_path(function_path)
    if not callable(function):
        return function
    f_args = list_function_arguments(function)

    # convert --arg1 val1 --arg2 --arg3 val3 in {"arg1": val1, "arg2": True, "arg3", val3}
    pos_args, parsed_args = parse_args(args)

    # search if commandline args are for function arguments
    kwargs = {}
    for arg in parsed_args.keys():
        if arg != "config" and arg in f_args:
            kwargs[arg] = parsed_args[arg]
            del parsed_args[arg]

    # If the function has a "config" argument of type (or subtype) micropype.Config
    if "config" in f_args and issubclass(f_args["config"], Config):
        # And if the second argument is a JSON file, load the config file
        if "config" in parsed_args and parsed_args["config"].endswith(".json"):
            conf = f_args["config"](parsed_args["config"])
            del parsed_args["config"]
        # Else init the Config from nothing
        else:
            conf = type(f_args["config"])()
        # Then use command line arguments to override default or loaded config
        conf = override_config_with_args(conf, parsed_args)

        # Finally run the function
        return function(*pos_args, config=conf, **kwargs)
    else:
        return function(*pos_args, **kwargs)
