import subprocess
from typing import List, Union

from src.helpers.data_helper import GCPCommandResponse


def run_subprocess(command: Union[List[str], str]) -> GCPCommandResponse:
    res = subprocess.run(
        args=command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,

    )
    response = GCPCommandResponse(
        status_code=res.returncode,
        output=(res.stdout or "").strip(),
        error=(res.stderr or "").strip()
    )
    return response
