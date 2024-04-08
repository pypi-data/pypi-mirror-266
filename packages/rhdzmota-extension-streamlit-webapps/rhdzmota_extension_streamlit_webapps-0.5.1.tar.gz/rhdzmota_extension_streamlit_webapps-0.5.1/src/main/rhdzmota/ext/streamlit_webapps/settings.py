import os
import enum


class Env(enum.Enum):
    EXT_APP_NAME = os.environ.get(
        "EXT_APP_NAME",
        default="streamlit_webapps",
    )
