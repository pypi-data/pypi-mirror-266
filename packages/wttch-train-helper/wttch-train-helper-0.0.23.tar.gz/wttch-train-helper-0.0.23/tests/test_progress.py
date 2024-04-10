import unittest
import time

from wth.utils.progress import Progress
from torch.utils.data import Dataset, DataLoader


class TestProgress(unittest.TestCase):
    def test_progress(self):
        with Progress(total=1000) as progress:
            for i in range(1000):
                time.sleep(0.01)
                progress.train_result(0.01, 0.02)

    def test_torch_progress(self):
        class _Dataset(Dataset):
            def __init__(self):
                super().__init__()

            def __len__(self):
                return 100 * 64

            def __getitem__(self, idx):
                return idx

        dataset = _Dataset()
        dataloader = DataLoader(dataset, shuffle=True, batch_size=64)

        progress = Progress(dataloader)
        for data in progress:
            time.sleep(0.02)
            progress.train_result(0.02)
