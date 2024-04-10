import subprocess  # nosec
import typing
from pathlib import Path
from typing import Optional


class Command:
    """
    This class is a wrapper around the subprocess module.
    It is used to run commands in the shell.
    """

    def __init__(self, cmd_list: typing.List, cwd: Optional[Path] = None) -> None:
        self._cmd_list = cmd_list
        self._cwd = cwd

    def run(self) -> subprocess.CompletedProcess:
        # Please note that the following line, has security checks disabled.
        # Some security tips:
        #   - https://security.openstack.org/guidelines/dg_use-subprocess-securely.html
        #   - https://security.openstack.org/guidelines/dg_avoid-shell-true.html
        #   - https://docs.python.org/3.12/library/subprocess.html#security-considerations
        completed_process = subprocess.run(
            self._cmd_list,
            capture_output=True,
            text=True,
            check=True,
            cwd=self._cwd,
        )  # nosec

        return completed_process
