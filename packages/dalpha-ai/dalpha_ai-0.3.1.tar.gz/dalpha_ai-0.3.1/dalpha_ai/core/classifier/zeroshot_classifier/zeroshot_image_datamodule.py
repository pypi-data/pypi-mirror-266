import pandas as pd
from torch.utils.data import Dataset
from typing import List
import re


class TextDataset(Dataset):
    def __init__(self, text_list: List[str], text_prompt: str):
        """
        Text Dataset

        Args:
            text_list (List[str]): list of text input
            text_prompt (str): text prompt
        """
        super().__init__()
        self.text_list = text_list
        self.text_prompt = text_prompt

    def __getitem__(self, idx):
        text = self.text_list[idx]
        if bool(re.match("^[a-zA-Z\s><.,!?|]*$", text)):
            text = self.text_prompt.format(text)
        else:
            raise ValueError(
                f"Failed to create embedding vectors from text '{text}', The text must be composed only of English letters and ' ' ',' '.' '|' '>' '<' '!' '?'."
            )

        return text

    def __len__(self):
        return len(self.text_list)


class ImageDataset(Dataset):
    """
    Image Dataset

    Args:
        img_path_list (List[str]): list of image path
    """

    def __init__(self, img_path_list):
        super().__init__()
        self.img_path_list = img_path_list

    def __getitem__(self, idx):
        input_img_path = self.img_path_list[idx]

        return input_img_path

    def __len__(self):
        return len(self.img_path_list)


class ImageClassifierDataset(Dataset):
    """
    Image Classifier Dataset

    Args:
        data (pd.DataFrame): dataframe of image path and label
    """

    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self.img_path_list = data["img_path"].tolist()
        self.label_list = data["label"].tolist()

    def __getitem__(self, idx):
        input_img_path = self.img_path_list[idx]
        label = self.label_list[idx]

        return input_img_path, label

    def __len__(self):
        return len(self.label_list)
