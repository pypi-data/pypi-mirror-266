"""Convert feedback dict into text.

Note that the configuration is loaded when the function gets called. This is
because we have to ensure the toml file has been parsed.

"""


def formatter(feedback_dict: dict[str, list[str]], *, template) -> str:
    """Convert feedback dict into text.

    Within a question, the list of its feedback is joined by `one_sep`. It will
    be converted to text using `one_template`. There are two possible keys:
    `question` and `text`.

    Across questions, the list of feedback of all questions is joined by
    `full_sep`. It will be converted to text using `full_template`. There is
    only one possible key: `text`.

    """
    one_sep = template["one_separator"]
    one_template = template["one"]
    full_sep = template["full_separator"]
    full_template = template["full"]

    full_l = []
    for qn in feedback_dict:
        one_text = one_template.format(
            question=qn,
            text=one_sep.join(feedback_dict[qn])
        )
        full_l.append(one_text)
    full_text = full_sep.join(full_l)
    feedback = full_template.format(text=full_text)
    return feedback


def no_auto_feedback(
        need_expert: dict[str, dict[str, str]],
        *,
        template
) -> dict[str, list[str]]:
    """State that no feedback is available.

    If a question does not have automated feedback, then
    `not_available_feedback` will be used. There is only one possible key:
    `question`.

    """
    not_available_feedback = template["not_available"]

    fb_dict = {}
    for qn in need_expert:
        fb_dict |= {qn: [not_available_feedback.format(question=qn)]}
    return fb_dict
