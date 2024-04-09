from micropype.commandline import override_config_with_args, parse_args, run_function_from_commandline
from micropype.config import Config
from micropype.utils import datetime_str


class DBConfig(Config):
    path: str

class NamedDBConfig(DBConfig):
    name: str = "unknown"

class ExConfig(Config):
    db: NamedDBConfig
    param1: float = 1.0
    step1: bool = False
    step2: bool = False
    step3: bool = False


testing_args = [
    "arg1", "arg2",
    "--param1", "1.2",
    "--step3",
    "--db.path", "/path/to/a/file.txz"
]

def test_parse_args():
    args, kwargs = parse_args(testing_args)

    assert("arg1" in args)
    assert("arg2" in args)
    assert("param1" in kwargs)
    assert("step3" in kwargs)
    assert("db.path" in kwargs)
    assert(kwargs["param1"] == float(testing_args[3]))
    assert(kwargs["db.path"] == testing_args[6])

def test_override_config_with_args():
    cfg = ExConfig()
    cfg2 = override_config_with_args(
        cfg,
        parse_args(testing_args)[1]
    )

    assert(cfg2.db.name == "unknown")
    assert(cfg2.db.path == testing_args[6])
    assert(cfg.step1 == cfg2.step1)
    assert(cfg.step2 == cfg2.step2)
    assert(type(cfg2.step3) == bool)
    assert(cfg2.step3 == True)


def test_run_with_only_positionnals():
    dt_str = datetime_str()[:8]
    assert(dt_str == run_function_from_commandline("micropype.utils.datetime_str")[:8])
