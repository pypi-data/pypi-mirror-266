import importlib
import __main__

from clearconf.utils.file import find_cconf_config, load_cconf_config
from clearconf.utils.conf import get_configs, get_default


cconf_conf_path = find_cconf_config()

if cconf_conf_path is None:
    raise ImportError("Couldn't find clearconf configuration file.\n"
          "Run 'cconf init' in your project root directory.")

cconf_conf = load_cconf_config(cconf_conf_path)
config_list = get_configs(cconf_conf)

try:
    usr_conf = get_default(cconf_conf, __main__.__file__.split('/')[-1])
    assert usr_conf is None or usr_conf[-3:] != '.py'
except AttributeError:
    usr_conf = None

if usr_conf is None:
    print('You can specify a default configuration with "cconf default"')
    for i, c in enumerate(config_list):
        print(f'{i}: {c}')

    print('Choose a configuration file:')
    k = input()
    usr_conf = config_list[int(k)]


Config = importlib.import_module(f'{__package__}.{usr_conf}').Config
Config.init()
