import subprocess
import os
from typing import Optional

from .logger_util import logger
from .path_util import PathUtil


class ExecuteJavaFile:

    @staticmethod
    def execute_java_file(path: Optional[str], java_file: Optional[str]):
        command = f'java -cp {path} {java_file}'
        run_process = os.popen(command).read()
        out = run_process.split('\n')[0]
        if out:
            logger.info(f"Java program output: {out}")
            return out
        else:
            logger.error(
                f'Error running java program:\n {run_process}')
            return []
