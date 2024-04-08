"""
all the OpenGL related codes are here. use Renderer class to render scenes.
.. attention:: OpenGL renderer might not work with some graphic drivers (AMD deivers in particular).
.. attention:: only one opengl context can be created at one single session. so we should not have multiple instances of Renderer.
"""

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from .scene_tools import *

from . import VERTEX_SHADER_PATH, FRAGMENT_SHADER_PATH

qtapp = QtWidgets.QApplication.instance()  # gets running qapplication
if qtapp is None:  # if there is no qapplication running, create one.
    qtapp = QtWidgets.QApplication(sys.argv)


class Renderer(QtCore.QObject):
    background_color = [1.0, 1.0, 1.0, 1.0]  # rendering background color RGBA. Each value between 0 and 1.
    shading = "flat"  # rendering shading mode. can be set using `set_shading` method.

    def __init__(self):
        """
        Attributes:
            scene: an instance of the `Scene` class.
            fbo: offscreen frame buffer object where all renderings happen.
            vao_dict: opengl vertex array object for each actor in the scene.
            vbo_dict: opengl vertex buffer object for each actor in the scene.
            texture_dict: texture objects for each actor in the scene.
            shader_program: opengl shader program which contains vertex shader and fragment shader internally.
            gl_locations: a dictionary which contains the location of each variable defined in vertex shader and fragment shader.
        """
        super(Renderer, self).__init__()
        self.scene = None
        self.fbo = None
        self.vao_dict = {}
        self.vbo_dict = {}
        self.texture_dict = {}
        self.shader_program = None
        self.gl_locations = None
        self._init_opengl()
        self._setup_shaders()
        self._setup_gl_locations()
        self.set_resolution(1024, 1024)  # sets a default resolution as well as creating the FBO.
        self.set_shading("flat")  # sets default shading as flat.

    def _init_opengl(self):
        """
        initializing opengl context and gl calls.
        attention:: any change to the specified versions in this function might result in OpenGL malfunction.
        """
        self.profile = QtGui.QOpenGLVersionProfile()
        self.profile.setVersion(2, 1)

        self.format = QtGui.QSurfaceFormat()
        self.format.setVersion(2, 0)
        self.format.setSamples(8)
        self.format.setProfile(QtGui.QSurfaceFormat.CompatibilityProfile)

        self.context = QtGui.QOpenGLContext()
        self.context.setFormat(self.format)
        assert self.context.create(), "OpenGl context creation failed."

        self.surface = QtGui.QOffscreenSurface()
        self.surface.setFormat(self.format)
        self.surface.create()

        self.context.makeCurrent(self.surface)

        self.gl = self.context.versionFunctions(self.profile)
        self.gl.initializeOpenGLFunctions()

    def _setup_shaders(self):
        """
        sets up vertex shader and fragment shader.
        this function loads the shaders from `shaders/vertex_shader.vsh` and `fragment_shader.fsh` files.
        """

        def read_shader_file(path: str):
            with open(path) as f:
                shader_source = f.read()
            return str.encode(shader_source)

        self.shader_program = QtGui.QOpenGLShaderProgram(self)
        self.shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Vertex, read_shader_file(VERTEX_SHADER_PATH))
        self.shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Fragment, read_shader_file(FRAGMENT_SHADER_PATH))
        self.shader_program.link()

    def _setup_gl_locations(self):
        """
        sets up a dictionary containing variables' locations in the shaders.
        """
        self.gl_locations = {
            "pos": 0,  # according to vertex shader layout
            "in_tex_coord": 1,  # according to vertex shader layout
            "in_vert_normal": 2,  # according to vertex shader layout
            "color": self.shader_program.uniformLocation("color"),
            "scale": self.shader_program.uniformLocation("scale"),
            "tex": self.shader_program.uniformLocation("tex"),
            "model_M": self.shader_program.uniformLocation("model_M"),
            "view_M": self.shader_program.uniformLocation("view_M"),
            "projection_M": self.shader_program.uniformLocation("projection_M"),
            "opacity": self.shader_program.uniformLocation("opacity"),
            "tex_blend_fac": self.shader_program.uniformLocation("tex_blend_fac"),
            "simple_shading": self.shader_program.uniformLocation("simple_shading"),
        }

    def bind_scene(self, scene: Scene = None, force=False):
        """
        this function loads scene's data to OpenGL's buffers. in other words, it binds a scene to opengl renderer.
        this operation needs to be done before calling render() function.
        args:
            scene: an instance of the `Scene` class. contents of scene load on opengl buffers.
            force: normally, it wouldn't be efficient to bind a scene if it's already bounded. however, sometimes depending on the application, we need to force them to load again.
        """
        if self.scene == scene and not force:  # if the scene is already bound and force is false, return.
            return
        self.scene = scene
        for act in self.vao_dict.keys():  # clear already occupied buffer to prevent memomry issues.
            self.vbo_dict[act].destroy()
            try:
                self.texture_dict[act].destroy()
            except KeyError:
                pass
            self.vao_dict[act].destroy()
        self.vao_dict = {}
        self.vbo_dict = {}
        self.texture_dict = {}
        if scene:
            self._setup_vao()
            self._setup_textures()

    def _setup_textures(self):
        """
        load textures given in ModelBase.texture into OpenGL buffers.
        texture objects go into self.texture_dict.
        """
        self.gl.glActiveTexture(self.gl.GL_TEXTURE0)
        for act in self.scene.actors:
            if act.texture:
                im = act.texture()
                if im.ndim == 2:
                    image = QtGui.QImage(
                        im,
                        im.shape[1],
                        im.shape[0],
                        im.shape[1] * 1,
                        QtGui.QImage.Format_Grayscale8,
                    )
                elif im.ndim == 3:
                    image = QtGui.QImage(
                        im,
                        im.shape[1],
                        im.shape[0],
                        im.shape[1] * 3,
                        QtGui.QImage.Format_RGB888,
                    )
                else:
                    raise Exception("Texture is not valid. Texture must be a MxN or MxNx3 array.")
                tex_obj = QtGui.QOpenGLTexture(QtGui.QOpenGLTexture.Target2D)
                tex_obj.setData(image)
                self.texture_dict[act] = tex_obj

    def _setup_vao(self):
        """
        Retrieves mesh data from `ModelBase.mesh` as a `Nx8` array. Then, this mesh data will be loaded into OpenGL VBOs.
        Finally, we'll create VAOs to specify where the point coordinates, texture coodinate and normal vectors are stored inside the VBOs.
        In fact, for each actor in the scene, we create a seperate VBO and VAO.
        """
        for act in self.scene.actors:
            data = act.mesh
            assert (
                data.shape[1] == 8
            ), "We expect the vertex data to have 8 columns (3 for position, 2 for texture coords, 3 for normals)"

            self.vao_dict[act] = QtGui.QOpenGLVertexArrayObject(self)
            vao = self.vao_dict[act]
            assert vao.create(), "VAO creation failed"
            vao.bind()

            self.vbo_dict[act] = QtGui.QOpenGLBuffer(QtGui.QOpenGLBuffer.VertexBuffer)
            vbo = self.vbo_dict[act]
            assert vbo.create(), "VBO creation failed"
            vbo.bind()
            vbo.allocate(data, data.nbytes)

            stride = data[0, :].nbytes

            self.shader_program.enableAttributeArray(self.gl_locations["pos"])
            self.shader_program.setAttributeBuffer(self.gl_locations["pos"], self.gl.GL_FLOAT, 0, 3, stride)

            self.shader_program.enableAttributeArray(self.gl_locations["in_tex_coord"])
            self.shader_program.setAttributeBuffer(
                self.gl_locations["in_tex_coord"],
                self.gl.GL_FLOAT,
                data[0, 0:3].nbytes,
                2,
                stride,
            )

            self.shader_program.enableAttributeArray(self.gl_locations["in_vert_normal"])
            self.shader_program.setAttributeBuffer(
                self.gl_locations["in_vert_normal"],
                self.gl.GL_FLOAT,
                data[0, 0:5].nbytes,
                3,
                stride,
            )

            vbo.release()
            vao.release()

    def render(self, cam_index) -> np.ndarray:
        """
        renders the scene bound by `bind_scene`.
        args:
            cam_index: camera index in `self.scene.cameras` list. The rendering will be done from this camera's point of veiw.
        returns:
            a MxNx3 array as the rendered image.
        """
        self.shader_program.bind()
        self.fbo.bind()

        self.gl.glClearColor(*self.background_color)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)

        # to have a proper rendering of transparent objects, we have to follow an order:
        # draw non-transparent actors first
        for act in self.scene.actors:
            if act.visible and act.opacity == 1:
                self._draw_actor(act, self.scene.cameras[cam_index])

        # then, draw transparent actors; sorted furthest (from camera) to nearest.
        self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glCullFace(self.gl.GL_BACK)
        self.gl.glDepthMask(self.gl.GL_FALSE)
        for act in self.zsorting(
            self.scene.actors,
            self.scene.cameras[cam_index].lookat_screen_mat4(),
        ):
            if act.visible and act.opacity < 1:
                self._draw_actor(act, self.scene.cameras[cam_index])
        self.gl.glDisable(self.gl.GL_CULL_FACE)
        self.gl.glDepthMask(self.gl.GL_TRUE)

        rendered_scene = self._capture_fbo()

        self.fbo.release()
        self.shader_program.release()

        return rendered_scene

    @staticmethod
    def zsorting(actors: List["ModelBase"], cam_view_mat):
        """
        sorts actors in order of furthest to nearest from camera. this function is used for proper rendering of transparent objects.
        args:
            actors: list of actors to be sorted.
            cam_view_mat: camera's view transformation matrix.
        returns:
            list of sorted actors.
        """
        mc = [act.get_mesh_center() for act in actors]
        mcn = np.ones((len(mc), 4))
        mc = np.array(mc)
        mcn[:, 0:3] = mc
        z = (cam_view_mat @ mcn.transpose())[2, :]
        i = np.argsort(z)
        return [actors[ii] for ii in i]

    def _draw_actor(self, act: ModelBase, cam: Camera):
        """
        renders an individual actor.
        args:
            act: the actor to be rendered. Notice that this actor must be bound to the renderer before.
            cam: the camera that rendering should be done from.
        """
        self.shader_program.setUniformValue(self.gl_locations["scale"], 1.0)  # no scaling
        self.shader_program.setUniformValue(
            self.gl_locations["model_M"],
            QtGui.QMatrix4x4(act.get_model_matrix().flatten()),
        )
        self.shader_program.setUniformValue(
            self.gl_locations["projection_M"],
            QtGui.QMatrix4x4(cam.default_proj_mat4().flatten()),
        )
        self.shader_program.setUniformValue(
            self.gl_locations["view_M"],
            QtGui.QMatrix4x4(cam.lookat_screen_mat4().flatten()),
        )

        prev_shading = self.shading  # stores current shading mode
        if act.outline_mode:  # if outline_mode is enabled for an actor, then it must be rendered with `NoShading`.
            self.set_shading("noshading")

        self.gl.glPolygonMode(
            self.gl.GL_FRONT_AND_BACK,
            self.gl.GL_LINE if act.wire_frame else self.gl.GL_FILL,
        )  # set wireframe mode or fill mode. also set line_width.
        self.gl.glLineWidth(act.line_width)

        self.gl.glActiveTexture(self.gl.GL_TEXTURE0)  # we only use texture unit 0
        self.shader_program.setUniformValue(self.gl_locations["tex"], 0)
        self.gl.glBindTexture(self.gl.GL_TEXTURE_2D, 0)
        try:  # some actors might not have textures. so we use try statement.
            self.texture_dict[act].bind()
        except KeyError:
            pass
        self.shader_program.setUniformValue(self.gl_locations["color"], *act.color)
        self.shader_program.setUniformValue(self.gl_locations["opacity"], act.opacity)
        self.shader_program.setUniformValue(self.gl_locations["tex_blend_fac"], act.texture_blend_fac)

        self.vao_dict[act].bind()
        self._draw_array(self.gl.GL_TRIANGLES, act.nvertices, act.outline_mode)
        self.set_shading(prev_shading)  # set shading back to its previous mode.
        try:
            self.texture_dict[act].release()
        except KeyError:
            pass
        self.vao_dict[act].release()

    def _draw_array(self, primitives, count, outline_mode=False):
        """
        draws the bound VAO. depending on outline_mode, only the outline or the surface will be rendered.
        args:
            primitives: specifies the primitive type for drawing the VAO.
            count: specifies the number of VAO contents to be drawn.
            outline_mode: enable or disable out_line mode.
        ..Warning:: Users must match the inside of the outline!
        """
        if outline_mode:
            self.gl.glDepthMask(self.gl.GL_FALSE)
            self.gl.glEnable(self.gl.GL_STENCIL_TEST)
            # just reset everthing
            self.gl.glStencilFunc(self.gl.GL_ALWAYS, 1, 0xFF)
            self.gl.glStencilMask(0xFF)
            self.gl.glClear(self.gl.GL_STENCIL_BUFFER_BIT)
            # replace value when both depth and stencil test pass
            self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_REPLACE)
            # turn off colorbuffer and render the object to stencil buffer
            self.gl.glColorMask(self.gl.GL_FALSE, self.gl.GL_FALSE, self.gl.GL_FALSE, self.gl.GL_FALSE)
            self.gl.glDrawArrays(primitives, 0, count)
            # Render the wireframe object to the color buffer
            # this object will be larger because of linewidth
            # mask all parts that correspond to the stencil, so we really only get the outline
            self.gl.glStencilFunc(self.gl.GL_NOTEQUAL, 1, 0xFF)
            # turn off writing to stencil buffer
            self.gl.glStencilMask(0x00)
            self.gl.glColorMask(self.gl.GL_TRUE, self.gl.GL_TRUE, self.gl.GL_TRUE, self.gl.GL_TRUE)
            self.gl.glPolygonMode(self.gl.GL_FRONT, self.gl.GL_LINE)
            self.gl.glDrawArrays(primitives, 0, count)
            # reset stuff
            self.gl.glPolygonMode(self.gl.GL_FRONT, self.gl.GL_FILL)
            self.gl.glStencilFunc(self.gl.GL_ALWAYS, 1, 0xFF)
            self.gl.glDisable(self.gl.GL_STENCIL_TEST)
            self.gl.glDepthMask(self.gl.GL_TRUE)
        else:
            self.gl.glDrawArrays(primitives, 0, count)

    def _capture_fbo(self) -> np.ndarray:
        """
        captures the rendered scene available on FBO and converts it to a regular MxNx3 array.
        returns:
            a MxNx3 array representing the rendered scene.
        """

        def QImageToArr(incoming_image):
            size = incoming_image.size()
            s = incoming_image.bits().asstring(size.width() * size.height() * incoming_image.depth() // 8)  # format 0xffRRGGBB
            arr = np.frombuffer(s, dtype=np.uint8).reshape((size.height(), size.width(), incoming_image.depth() // 8))
            arr = np.array(arr[..., 0:3])
            arr[..., [0, 2]] = arr[..., [2, 0]]
            return np.array(arr).astype(np.uint8)

        return QImageToArr(self.fbo.toImage())

    def set_resolution(self, width, height):
        """
        sets rendering resolution as well as creating FBO.
        args:
            width: width of the final image (number of columns) in pixels.
            height: height of the final image (number of rows) in pixels.
        """
        self.fbo = QtGui.QOpenGLFramebufferObject(width, height, target=QtGui.QOpenGLTexture.Target2D)
        self.fbo.setAttachment(QtGui.QOpenGLFramebufferObject.CombinedDepthStencil)

        self.gl.glClearColor(*self.background_color)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_BLEND)  # enable blend function in order to have transparancy
        self.gl.glBlendFunc(self.gl.GL_SRC_ALPHA, self.gl.GL_ONE_MINUS_SRC_ALPHA)  # determine blend function
        self.gl.glEnable(self.gl.GL_LINE_SMOOTH)
        self.gl.glHint(self.gl.GL_LINE_SMOOTH_HINT, self.gl.GL_NICEST)

        self.gl.glViewport(0, 0, width, height)

    def set_shading(self, shading_type="flat"):
        """
        sets shading mode.
        args:
            shading_type: either `Flat` or `NoShading`.
            `Flat` shading is basically when we use lights and normal vectors for shading as well as textures.
             On the other hand, `NoShading` renders all object with their plain colors only; no light and textures.
        """
        self.shader_program.bind()
        if shading_type.lower() == "flat":
            self.shader_program.setUniformValue(self.gl_locations["simple_shading"], False)  # means: don't use simple shading
            self.shading = "flat"
        elif shading_type.lower() == "noshading":
            self.shader_program.setUniformValue(self.gl_locations["simple_shading"], True)  # means: use simple shading
            self.shading = "noshading"
        else:
            raise Exception(f"shading_type '{shading_type}' is not valid.")

    def get_opengl_info(self):
        """
        gets system's current OpenGL setup. this function is helpful when you need to know which graphic driver is responsible for executing OpenGL functions.
        """
        info = {
            "Vendor": self.gl.glGetString(self.gl.GL_VENDOR),
            "Renderer": self.gl.glGetString(self.gl.GL_RENDERER),
            "OpenGL Version": self.gl.glGetString(self.gl.GL_VERSION),
            "Shader Version": self.gl.glGetString(self.gl.GL_SHADING_LANGUAGE_VERSION),
        }
        return info


if __name__ == "__main__":
    pass
