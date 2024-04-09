import os
import sys
import textwrap
import importlib
from typing import Optional
from dataclasses import dataclass

from rhdzmota.utils.misc import create_temporal_file


@dataclass(frozen=True, slots=True)
class Runner:

    @property
    def package_version(self) -> str:
        from importlib.metadata import version
        return version("streamlit")

    @property
    def streamlit_climodule_refname(self) -> str:
        # TODO: Can we provide a more accurate reference version?
        return "streamlit.web.cli" if self.package_version > "1.11.1" else "streamlit.cli"

    @property
    def streamlit_climodule(self):
        import importlib

        return importlib.import_module(self.streamlit_climodule_refname)

    def start_from_file(self, filepath: str, *args, **kwargs):
        if not os.path.exists(filepath):
            raise ValueError("Target script doesn't exists: %s", filepath)
        # Make streamlit CLI think it's been executed via a terminal
        sys.argv = ["streamlit", "run", filepath] + [*args] + [
            line
            for key, val in kwargs.items()
            for line in [key, val]
        ]
        self.streamlit_climodule.main()

    def start_from_content(self, content: str, path: Optional[str] = None):
        filepath = create_temporal_file(
            content=content,
            suffix=".py",
            path=path,
        )
        return self.start_from_file(filepath=filepath)

    def start_from_function_refname(
            self,
            function_name: str,
            module_name: str,
            temp_filepath: Optional[str] = None,
    ):
        content = textwrap.dedent(
            f"""
            from {module_name} import {function_name}

            if __name__ == "__main__":
                {function_name}()
            """
        )
        return self.start_from_content(content=content, path=temp_filepath)
