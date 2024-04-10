"""Parse configurations."""

import sys

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Access to configuration values."""

    config_dict: dict[str, dict]
    feature_dict: dict[str, dict]
    feedback_template: dict[str, dict]

    def __init__(self, toml_f_str: str):
        self.config_dict = tomllib.loads(Path(toml_f_str).read_text())
        self.feature_dict = self.config_dict["feature"]
        self.feedback_template = self.config_dict["template"]
