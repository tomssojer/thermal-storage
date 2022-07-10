from pathlib import Path
import os

ROOT_DIRECTORY = Path(__file__).parent.absolute().parent.absolute()
LOG_DIRECTORY = "logs"
LOG_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY, LOG_DIRECTORY)