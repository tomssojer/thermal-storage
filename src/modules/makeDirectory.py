from pathlib import Path
import os

ROOT_DIRECTORY = Path(__file__).parent.parent.parent.absolute()
LOG_DIRECTORY = "logs"
LOG_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY, LOG_DIRECTORY)

def getDirectoryName(directory):
    # Change to specified directory
    os.chdir(directory)

    dirName = input("Choose a name for the directory: ")
    dirPath = os.path.join(directory, dirName)
    try:
        os.mkdir(dirPath)
    except OSError:
        print("Try a different one")
        getDirectoryName(directory)

    return dirPath

def makeDir():
    # Check if such dir already exists
    if not os.path.exists(LOG_DIRECTORY_PATH):
        os.makedirs(LOG_DIRECTORY_PATH)
    return getDirectoryName(LOG_DIRECTORY_PATH)