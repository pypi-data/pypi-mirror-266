# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License

from onnxruntime_genai import _dll_directory

try:
    # Try importing onnxruntime_genai. If an ImportError is raised,
    # it could be because the cuda dlls could not be found on windows.
    # Try adding the cuda dlls path to the dll search directory
    # and import onnxruntime_genai again.
    from onnxruntime_genai.onnxruntime_genai import *
except ImportError:
    _dll_directory.add_dll_directory()
    from onnxruntime_genai.onnxruntime_genai import *

__version__ = "0.1.0"
