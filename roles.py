import json
from collections import namedtuple


Role = namedtuple(
    "Role", ["name", "held_in_conjunction", "number_of_positions"]
)


def decode_hook(o):
    if "name" in o:
        return Role(
            o["name"],
            o["held_in_conjunction"],
            o["number_of_positions"],
        )
    return o


def load_roles(roles_fp):
    with open(roles_fp) as infile:
        return json.load(infile, object_hook=decode_hook)
