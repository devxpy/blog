import string
from random import choices


def get_context(env):
    env.globals.update(
        {
            "randid": lambda: "".join(choices(string.ascii_lowercase, k=8)),
            "jsfiles": set(),
            "cssfiles": set(),
        }
    )

    return {
        "posts": [
            {
                "path": "/posts/missing-type-checker",
                "time": 1587906406.8684,
                "title": "Python's missing runtime type checker",
            },
            {
                "path": "/posts/infinite-scrolling",
                "time": 1588062591.499132,
                "title": "Continuous, infinite scrolling with wrap-around in HTML/CSS/JS",
            },
        ]
    }
