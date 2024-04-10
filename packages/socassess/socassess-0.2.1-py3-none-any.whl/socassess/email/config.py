from dataclasses import dataclass

from ..config import Config


@dataclass
class EmailConfig:
    """Contain email configurations."""

    account: str
    password: str
    email_from: str
    email_to: str
    smtp_server: str
    subject: str
    email_body: str
    initial_reply: str

    def __init__(self, config: Config):
        config_dict = config.config_dict

        assert "email" in config_dict, "cannot find email configurations in socassess.toml"  # noqa: E501
        assert "account" in config_dict["email"], "cannot find email.account configurations in socassess.toml"  # noqa: E501
        assert "content" in config_dict["email"], "cannot find email.content configurations in socassess.toml"  # noqa: E501

        email_account_dict = config_dict["email"]["account"]
        email_content_dict = config_dict["email"]["content"]

        self.account = email_account_dict["account"]
        self.password = email_account_dict["password"]
        self.email_from = email_account_dict["from"]
        self.email_to = email_account_dict["to"]
        self.smtp_server = email_account_dict["smtp_server"]

        self.subject = email_content_dict["subject"]
        self.email_body = email_content_dict["email_body"]
        self.initial_reply = email_content_dict["initial_reply"]
