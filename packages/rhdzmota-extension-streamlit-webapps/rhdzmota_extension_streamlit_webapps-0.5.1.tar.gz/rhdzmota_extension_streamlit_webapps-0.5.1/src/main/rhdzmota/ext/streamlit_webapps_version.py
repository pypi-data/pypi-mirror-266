import os

from rhdzmota.version import Version


version = Version.from_path(
    name="streamlit_webapps_version",
    dirpath=os.path.dirname(__file__),
)
