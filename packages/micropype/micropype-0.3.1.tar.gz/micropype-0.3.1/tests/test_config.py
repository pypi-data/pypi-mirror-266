import tempfile
import os.path as op

import json
from micropype.config import Config


@Config.register
class SubConfig(Config):
    name:   str = "Albert"
    age:    float

@Config.register
class AConfig(Config):
    num:        float = .3
    foo:        dict
    subject:    SubConfig


def test_config():
    # Create config from dict
    conf = {
        "paul": "jeje",
        "foo": {"item1": 0.1, "item2": 0.2},
        "subject": {
            "name": "ciceron",
            "age":  12
        }
    }

    config = AConfig(**conf)
    assert(config.num == .3)
    assert(config.subject.age == 12)

    # Export as json
    tmp_dir = tempfile.TemporaryDirectory()
    json_f = op.join(tmp_dir.name, "config.json")
    config.to_json(json_f)

    js = json.load(open(json_f, 'r'))
    assert(js['num'] == .3)

    # Re-import from json
    jconfig = AConfig(json_f)
    assert(jconfig.foo['item2'] == config.foo['item2'])
    assert(jconfig.num == config.num)
    assert(jconfig.subject.age == config.subject.age)
    assert(jconfig.subject.name == config.subject.name)
