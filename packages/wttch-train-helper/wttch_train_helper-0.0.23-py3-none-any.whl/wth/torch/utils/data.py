from torch.utils.data import Dataset, random_split, DataLoader

from wth.torch import Config


class TrainAndTestDataLoader:
    def __init__(self, dataset: Dataset, train_rate: float = 0.9, config: Config = None):
        self.dataset = dataset
        if train_rate < 0 or train_rate > 1:
            raise ValueError(f"train_rate should be between 0 and 1, got {train_rate}")
        batch_size = config.batch_size if config is not None else 64

        train_dataset, test_dataset = random_split(self.dataset, lengths=[train_rate, 1 - train_rate])
        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        self.test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
