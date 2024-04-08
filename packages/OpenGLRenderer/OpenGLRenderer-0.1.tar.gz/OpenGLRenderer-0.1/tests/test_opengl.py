import unittest
import os
from OpenGLRenderer import VERTEX_SHADER_PATH, FRAGMENT_SHADER_PATH, Renderer


class TestShader(unittest.TestCase):

    def test_vertex_shader_exist(self):
        file_path = VERTEX_SHADER_PATH
        file_exists = os.path.exists(file_path)
        self.assertTrue(file_exists, f"File '{file_path}' does not exist.")

    def test_fragment_shader_exist(self):
        file_path = FRAGMENT_SHADER_PATH
        file_exists = os.path.exists(file_path)
        self.assertTrue(file_exists, f"File '{file_path}' does not exist.")


class TestOpenGL(unittest.TestCase):

    def test_gl_info(self):
        renderer = Renderer()
        gl_info = renderer.get_opengl_info()
        self.assertNotEqual(gl_info["OpenGL Version"], "")
        self.assertNotEqual(gl_info["Shader Version"], "")


if __name__ == "__main__":
    unittest.main()
