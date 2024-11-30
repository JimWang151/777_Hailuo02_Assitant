# Made by Jim.Wang V1 for ComfyUI
import os
import subprocess
import importlib.util
import sys
import filecmp
import shutil

import __main__

python = sys.executable




from .Hailuo02 import GetPrompt

NODE_CLASS_MAPPINGS = {

    "GetPrompt": GetPrompt,
}


print('\033[34mHailuo02 Assistant Nodes: \033[92mLoaded\033[0m')