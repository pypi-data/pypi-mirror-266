"""This is an example of how a Config looks like.
    You can remove the parts that you don't need and add
    new sections as you please."""

from pathlib import Path
from clearconf import BaseConfig
from models import MLP
from datasets import ImageNet
from torch.optim import Adam
from torch.nn import BCEWithLogitsLoss

class Config(BaseConfig):
    name = Path(__file__).parts[-1]
    seed = 1234

    class Model(BaseConfig):
        architecture = MLP

        class Params(BaseConfig):
            num_layers = 16
            layers_dim = [96] * num_layers

    class Data(BaseConfig):
        input_dimension = 16384 * 2
        split = [0.1, 0.4, 0.5]
        noise_rate = 0.1
        tolerance = 0.001

        class DataSet(BaseConfig):
            dataset = ImageNet

            class Params(BaseConfig):
                root = './data/PCN'
                split = 'PCN.json'
                subset = 'train'
                length = None
                pick = [0]

        class DataLoader(BaseConfig):

            class Params(BaseConfig):
                batch_size = 1
                shuffle = False
                num_workers = 0
                pin_memory = True

    class Train(BaseConfig):
        loss_fn = BCEWithLogitsLoss()
        device = 'cuda'
        epochs = int(50_000)

        class Optim(BaseConfig):
            optim = Adam

            class Params(BaseConfig):
                lr = 0.0001

    class Logger(BaseConfig):
        active = False
        project = 'implicit-rep'
        task = 'input[0.1-0.4]-adam-(1)'


# if __name__ == '__main__':
#     Config.init()
#
#     from experiments import training as exp
#     exp.main()
