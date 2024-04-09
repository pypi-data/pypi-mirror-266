# encoding: utf-8

import os
from pathlib import Path
from typing import Dict


class Config:

    def __init__(self) -> None:
        self.verbose = False

    def to_dict(self) -> Dict:
        return {
            'verbose': self.verbose
        }


config = Config()

if __name__ == "__main__":
    pass
