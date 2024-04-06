import shutil
from pathlib import Path
import os

import clearconf
import typer

from clearconf.cli import defaults

from clearconf.utils.file import find_cconf_config, load_cconf_config, save_cconf_config
from clearconf.utils.stdout import print_list
from clearconf.utils.conf import get_configs

app = typer.Typer()
app.add_typer(defaults.app, name="defaults")

assets_path = Path(os.path.abspath(clearconf.__file__)).parent / "assets"


@app.command()
def init():
    cfg_root = Path('configs')
    if cfg_root.exists():
        print(f'Directory {cfg_root.as_posix()} already exists.')
    else:
        cfg_root.mkdir()
        shutil.copy(assets_path / 'init.py', cfg_root / '__init__.py')
        shutil.copy(assets_path / 'stub_conf.py', cfg_root)

    cconf_conf_path = Path('.clearconf')
    if cconf_conf_path.exists():
        print(f'File {cconf_conf_path.as_posix()} already exists.')
    else:
        cconf_conf_path.touch()

        cconf_conf = {
            'project_root': os.getcwd(),
            'conf_dir': cfg_root.as_posix(),
            'defaults': {}
        }

        save_cconf_config(cconf_conf, cconf_conf_path)

@app.command()
def list():
    cconf_conf_path = find_cconf_config()

    if cconf_conf_path is None:
        print("Couldn't find clearconf configuration file.\n"
              "Run 'cconf init' in your project root directory.")
        return

    cconf_conf = load_cconf_config(cconf_conf_path)
    config_list = get_configs(cconf_conf)

    print_list(config_list)


@app.callback()
def doc():
    """
    clearconf CLI can be used to initialized your
    project configurations.
    """


def main():
    app()
