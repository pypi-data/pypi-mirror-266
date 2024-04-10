from pathlib import Path
from typing import Final

from ..config import Config
from . import expert as se
from .config import EmailConfig


def attachments(draft_feedback: str,
                artifacts: Path):
    """Collect necessary attachments that should be included in the email.

    Returns
    -------
    attachments: list[dict[str, str]]

    """
    filelist = [
        {
            'data': draft_feedback.encode('utf-8'),
            'maintype': 'text',
            'subtype': 'txt',
            'filename': 'draft_feedback.txt'
        },
    ]
    attachments_list = artifacts / "_attachments.txt"
    if not attachments_list.is_file():
        return filelist

    with attachments_list.open() as flist:
        for line in flist:
            line = line.strip()
            attachment = artifacts / line
            filelist.append(
                {
                    'data': attachment.read_bytes(),
                    'maintype': 'text',
                    'subtype': 'text',
                    'filename': attachment.name + '.txt'
                },
            )
    return filelist


def email_feedback(
        need_expert: dict[str, dict[str, str]],
        current_fb_dict: Final[dict[str, dict[str, str]]],
        ansdir: Path,
        artifacts: Path,
        *,
        config: Config
) -> dict[str, list[str]]:
    """Fallback to human feedback if automated feedback cannot be produced."""
    fb_v = ['\n'.join(x) for x in current_fb_dict.values()]
    current_feedback = '\n---\n'.join(fb_v)

    attachs = attachments(
        current_feedback,
        artifacts,
    )

    email_config = EmailConfig(config)
    se.seek_expert_reply(
        # a list of dict
        attachments=attachs,
        config=email_config
    )

    email_dict = {}
    for qn in need_expert:
        if qn not in current_fb_dict:
            email_dict |= {qn: [f"{qn}: automated feedback is not available."]}
    email_dict |= {'_email': [email_config.initial_reply]}
    return email_dict
