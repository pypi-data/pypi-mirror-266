# clearconf
ClearConf is a library created to support easy and manageble python configuration. 
It consists in a python API (based on the `BaseConfig` class) which adds additional functionalities to
a configuration class, and in an optional **CLI tool** to simplify managing configurations.
## Installation
To install ClearConf just run
```
pip install clearconf
```
## API
### Example 1
A configuration file for a machine learning project could be structure as follow.
```python
from models import MLP
from datasets import ImageNet


class Config(BaseConfig):
    seed = 1234

    class Model:
        architecture = MLP

        class Params:
            num_layers = 16
            layers_dim = [96] * num_layers


    class Data:
        dataset = ImageNet

        class Params:
            root = './data/PCN'
            split = 'PCN.json'
            subset = 'train'
```

The training/test script can access the configuration simply by importing it:
```python
from configs import Config

Model = Config.Model
Data = Config.Data

model = Model.architecture(**Model.Params.to_dict())
dataset = Data.dataset(**Data.Params.to_dict())
```
### Example 2
It is also possible to simplify the configuration further using inheritance. For example the Model configuration seen before would look like this:
```python
from models import MLP

class Config(BaseConfig):
    seed = 1234

    class Model(MLP):
        num_layers = 16
        layers_dim = [96] * num_layers
```
The corresponding script is:
```python
from configs import Config

model = Config.Model()
```
> [!NOTE]
> The MLP class will be able to access the attributes set in the configuration as plain object attributes (e.g. self.num_layer)

## CLI
The first step to use clearconf would be to use the CLI tool in the root of your project to initialize it:
```
cconf init
```
This will generate a `config` directory where you will store your configurations and a `.clearconf` file used by ClearConf to keep track of configurations.
After this you can start populating your config directory. You can find examples of configuration files in the **Example** section.
> [!IMPORTANT]
> clearconf cli recursively recognize as configuration all python files ending with `_conf`

Finally you can import a generic configuration in your script as 
```python
from configs import Config
```
and use it as you please.

When the script is run, if a default configuration has been set via the CLI
```
cconf defaults add main.py test_conf.py
```
such configuration will be dynamically imported. 

Otherwise, clearconf will list all the available configuration and ask you to pick one.
```
0: example3_conf
1: example1_conf
2: example2_conf
3: example4_conf
Choose a configuration file:

```
