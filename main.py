import ffmpeg
from typing import Sequence
from pathlib import Path
from enum import StrEnum, auto
from collections import deque
from collections.abc import Generator
import re
from enum import Enum
import tempfile
import time
import os
import concurrent.futures

# Set custom paths for ffmpeg and ffprobe executables
# Get the absolute path of the current file
current_file_path = Path(__file__).resolve()

# Set the ./bin path to the PATH environment variable
bin_path = current_file_path.parent.parent / "bin"
os.environ["PATH"] = a = str(bin_path) + os.pathsep + os.environ["PATH"]
print(f"{current_file_path = }")
print(f"{a = }")
