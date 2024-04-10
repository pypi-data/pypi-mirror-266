"""Try OpenAI."""

import json
import textwrap

from openai import OpenAI

from ..config import Config
from .config import AIConfig


def ask(client, context, *, config: AIConfig):
    """Ask and get a response."""
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {
                "role": "system",
                "content": config.system_prompt,
            },
            {
                "role": "user",
                "content": context
            },
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        frequency_penalty=config.frequency_penalty,
        presence_penalty=config.presence_penalty
    )
    return response


def ai_feedback(
        need_expert: dict[str, dict[str, str]],
        *,
        config: Config
) -> dict[str, list[str]]:
    """Contain logic to seek AI feedback."""
    ai_dict = {}

    ai_config = AIConfig(config)
    client = OpenAI(api_key=ai_config.openai_key)

    for qn, context in need_expert.items():
        response = ask(client, json.dumps(context), config=ai_config)
        ai_fb = response.choices[0].message.content
        ai_fb = textwrap.fill(ai_fb, width=80)
        ai_dict |= {qn: [ai_config.feedback_template.format(question=qn,
                                                            feedback=ai_fb)]}
    return ai_dict
