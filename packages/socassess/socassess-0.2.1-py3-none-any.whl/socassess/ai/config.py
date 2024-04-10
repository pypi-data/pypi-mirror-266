import os
from dataclasses import dataclass

from ..config import Config


@dataclass
class AIConfig:
    """Contain AI configurations."""

    openai_key: str
    model: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penaltyre: float
    presence_penalty: float
    system_prompt: str
    feedback_template: str

    def __init__(self, config: Config):
        config_dict = config.config_dict

        assert "openai" in config_dict, "cannot find ai configurations in socassess.toml"  # noqa: E501

        ai_dict = config_dict["openai"]

        if "openai_key" in ai_dict:
            self.openai_key = ai_dict["openai_key"]
        else:
            self.openai_key = os.environ.get("OPENAI_API_KEY")

        self.model = ai_dict["model"]
        self.temperature = ai_dict["temperature"]
        self.max_tokens = ai_dict["max_tokens"]
        self.top_p = ai_dict["top_p"]
        self.frequency_penalty = ai_dict["frequency_penalty"]
        self.presence_penalty = ai_dict["presence_penalty"]
        self.system_prompt = ai_dict["system_prompt"]
        self.feedback_template = ai_dict["template"]
