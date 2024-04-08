import os
from pathlib import Path

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


VERTEX_SHADER_PATH = str(dir_path / Path("shaders/vertex_shader.glsl"))
FRAGMENT_SHADER_PATH = str(dir_path / Path("shaders/fragment_shader.glsl"))

from .renderer import Renderer
from .scene_tools import *
