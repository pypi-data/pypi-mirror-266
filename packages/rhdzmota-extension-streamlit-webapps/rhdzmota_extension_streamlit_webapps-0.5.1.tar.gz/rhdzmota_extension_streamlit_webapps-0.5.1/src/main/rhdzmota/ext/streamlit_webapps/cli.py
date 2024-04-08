from rhdzmota.interface.cli import CLIBase
from rhdzmota.ext.streamlit_webapps.runner import Runner


class CLI(CLIBase):

    @property
    def _streamlit_runner(self) -> Runner:
        return Runner()

    def run_from_file(
            self,
            path: str,
    ):
        return self._streamlit_runner.start_from_file(filepath=path)

    def run_from_refname(
            self,
            function_name: str,
            module_name: str,
    ):
        return self._streamlit_runner.start_from_function_refname(
            function_name=function_name,
            module_name=module_name,
        )
