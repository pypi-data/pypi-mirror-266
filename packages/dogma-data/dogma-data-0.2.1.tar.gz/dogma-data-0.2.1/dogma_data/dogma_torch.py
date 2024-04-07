from typing import Any

from pathlib import Path

from json import loads

import torch

from torch.utils.data import IterableDataset


class StreamShardedData(IterableDataset):
    def __init__(self, sharded_s3_path: Path | str) -> None:
        super().__init__()
        self.sharded_s3_path = Path(sharded_s3_path)
        self.index = self._gather_dataset_index()
    
    def _gather_dataset_index(self) -> dict[str, Any]:
        pass
        
