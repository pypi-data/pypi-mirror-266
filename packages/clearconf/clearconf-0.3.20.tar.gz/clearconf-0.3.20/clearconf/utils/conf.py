from clearconf.utils.file import find_cconf_config, load_cconf_config
from pathlib import Path


def get_configs(cconf_conf):
    config_list = []

    # List all files ending with _cfg in the cfg_root directory
    project_root = Path(cconf_conf['project_root'])
    config_root = project_root / Path(cconf_conf['conf_dir'])

    for file in config_root.rglob('*'):

        if file.suffix == '.py' and file.stem[-5:] == '_conf':
            config_list.append(file.relative_to(config_root).as_posix()[:-3])

    return config_list


def get_default(cconf_conf, script_name):
    default_confs = cconf_conf['defaults']

    for script in default_confs:
        if script == script_name:
            return default_confs[script]

    return None
