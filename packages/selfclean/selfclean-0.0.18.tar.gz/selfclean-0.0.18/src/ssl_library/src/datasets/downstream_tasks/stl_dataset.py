from typing import Callable, Optional

import numpy as np
import pandas as pd
import torchvision


class STL10Dataset(torchvision.datasets.STL10):
    """STL-10 dataset."""

    LBL_COL = "label"

    def __init__(
        self,
        root: str,
        split: str = "train",
        folds: Optional[int] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        download: bool = False,
        **kwargs
    ):
        super().__init__(
            root=root,
            split=split,
            folds=folds,
            transform=transform,
            target_transform=target_transform,
            download=download,
            **kwargs
        )
        # create the metadata
        self.meta_data = pd.DataFrame(
            np.arange(self.data.shape[0]), columns=["data index"]
        )
        self.meta_data["label"] = self.labels
        # global configs
        self.n_classes = len(self.classes)

    def __getitem__(self, idx: int):
        rets = super().__getitem__(index=idx)
        rets = (rets[0], "", rets[1])
        return rets
