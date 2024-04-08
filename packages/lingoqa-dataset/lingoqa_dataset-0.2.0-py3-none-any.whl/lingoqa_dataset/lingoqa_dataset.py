import os
import zipfile
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Tuple

import gdown
import pandas as pd
import torch
from torch import Tensor
from torch.utils.data import Dataset
from torchvision.io import read_image
from tqdm import tqdm


class DatasetInfo(ABC):
    gdown_object_id: str
    zip_filename: str = "images.zip"
    parquet_filename: str
    save_directory: str


class SceneryDatasetInfo(DatasetInfo):
    gdown_object_id = "1GiwWGfrM8pO27CYLu_9Uwtdcz0JoqHr7"
    parquet_filename = "train.parquet"
    save_directory = "scenery"


class ActionDatasetInfo(DatasetInfo):
    gdown_object_id = "1QQqBrR3uGDC05Zc11zMeui6Zzl7RvFZg"
    parquet_filename = "train.parquet"
    save_directory = "action"


class EvaluationDatasetInfo(DatasetInfo):
    gdown_object_id = "1oA7W8-Ej_uJEuUxZIjPP5K8hQGGzYsPq"
    parquet_filename = "val.parquet"
    save_directory = "evaluation"


class DatasetType(Enum):
    SCENARY = 0
    ACTION = 1
    EVALUATION = 2


class LingoQADataset(Dataset):
    lingoqa_dataset_root_dir: Path
    dataset_info: DatasetInfo
    database: pd.DataFrame
    transforms: Optional[Any] = None

    def __init__(self, type: DatasetType, transforms: Optional[Any] = None) -> None:
        self.transforms = transforms
        if type == DatasetType.SCENARY:
            self.dataset_info = SceneryDatasetInfo()
        elif type == DatasetType.ACTION:
            self.dataset_info = ActionDatasetInfo()
        elif type == DatasetType.EVALUATION:
            self.dataset_info = EvaluationDatasetInfo()
        else:
            raise Exception(
                "Dataset type should be scenary/action/evaluation. \
                    Please check type of the dataset."
            )
        self.lingoqa_dataset_root_dir = Path(
            os.environ.get("LINGOQA_DATASET_ROOT_DIR", "/tmp/lingoqa_dataset")
        ).joinpath(self.dataset_info.save_directory)
        self.download()
        self.unzip_images()
        self.read_database()

    def __getitem__(self, index: int) -> Tuple[Tensor, str, str]:
        images_tensor: List[Tensor] = []
        for image_path in self.database.iloc[index].loc["images"]:
            image_tensor = read_image(
                str(self.lingoqa_dataset_root_dir.joinpath(image_path))
            )
            if self.transforms:
                image_tensor = self.transforms(image_tensor)
            images_tensor.append(image_tensor)
        return (
            torch.cat(images_tensor, dim=0),
            self.database.iloc[index].loc["question"],
            self.database.iloc[index].loc["answer"],
        )

    def __len__(self) -> int:
        return len(self.database)

    def read_database(self):
        self.database = pd.read_parquet(
            self.lingoqa_dataset_root_dir.joinpath(self.dataset_info.parquet_filename)
        )
        print("Loading dataset succeeded.")
        print(self.database)

    def unzip_images(self):
        if not Path.exists(self.lingoqa_dataset_root_dir.joinpath("images")):
            with zipfile.ZipFile(
                self.lingoqa_dataset_root_dir.joinpath(self.dataset_info.zip_filename)
            ) as zf:
                for member in tqdm(zf.infolist(), desc="Extracting "):
                    zf.extract(member, self.lingoqa_dataset_root_dir)

    def dataset_downloaded(self) -> bool:
        return Path.exists(
            self.lingoqa_dataset_root_dir.joinpath(self.dataset_info.zip_filename)
        ) and Path.exists(
            self.lingoqa_dataset_root_dir.joinpath(self.dataset_info.parquet_filename)
        )

    def download(self):
        if not self.dataset_downloaded():
            os.makedirs(self.lingoqa_dataset_root_dir, exist_ok=True)
            gdown.download_folder(
                id=self.dataset_info.gdown_object_id,
                quiet=False,
                output=str(self.lingoqa_dataset_root_dir),
            )


if __name__ == "__main__":
    pass
