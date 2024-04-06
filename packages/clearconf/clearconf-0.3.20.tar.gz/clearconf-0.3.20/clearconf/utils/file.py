import os
from pathlib import Path
import json


def find_cconf_config():
    """
    Search for the .clearconf configuration file starting from the working directory and proceeding backwards.
    Stops looking the level before '/'.

    returns: pathlib.Path() of the .clearconf file
    """
    cconf_root = Path(os.getcwd())
    cconf_conf_path = None

    while cconf_root != Path('/'):
        cconf_conf_path = cconf_root / '.clearconf'

        if cconf_conf_path.exists():
            break

        cconf_conf_path = None
        cconf_root = cconf_root.parent

    return cconf_conf_path


def load_cconf_config(cconf_conf_path: Path):
    with cconf_conf_path.open('r') as f:
        cconf_conf = json.load(f)
    return cconf_conf


def save_cconf_config(cconf_conf: dict, cconf_conf_path: Path):
    with cconf_conf_path.open('w+') as f:
        json.dump(cconf_conf, f, indent=4)
        f.write('\n')

