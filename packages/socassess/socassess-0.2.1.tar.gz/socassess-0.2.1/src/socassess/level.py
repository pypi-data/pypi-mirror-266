from enum import IntEnum


class FeedbackLevel(IntEnum):
    """Provide the grain level of a feedback.

    If higher level feedback exists, lower level feedback will not be shown.

    """

    LOWEST = 10  # default
    LOW = 20
    MEDIUM = 30
    HIGH = 40
    HIGHEST = 50
    # only display this feedback and ignore feedback for all other questions
    SINGLE = 100
