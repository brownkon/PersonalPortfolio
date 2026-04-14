import sys
import os
import torch
print("Python:", sys.version)
print("Torch:", torch.__version__)
try:
    import flask
    import flask_cors
    import cv2
    import open3d
    import sklearn
    print("All dependencies present!")
except ImportError as e:
    print("Missing:", e)
