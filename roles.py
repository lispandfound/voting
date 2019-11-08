import json
from collections import namedtuple


Role = namedtuple(
    "Role", ["name", "held_in_conjunction", "number_of_positions"]
)


def decode_hook(o):
    """ Decode a role JSON entry into a Role namedtuple.
    The following JSON construction:
    {
        'name': 'Foo Manager',
        'held_in_conjunction': false,
        'number_of_positions': 1
    }
    Becomes Role('Foo Manager', false, 1)
    """
    if "name" in o:
        return Role(
            o["name"],
            o["held_in_conjunction"],
            o["number_of_positions"],
        )
    return o


def load_roles(roles_fp):
    """ Load roles from the roles JSON file. """
    with open(roles_fp) as infile:
        return json.load(infile, object_hook=decode_hook)
