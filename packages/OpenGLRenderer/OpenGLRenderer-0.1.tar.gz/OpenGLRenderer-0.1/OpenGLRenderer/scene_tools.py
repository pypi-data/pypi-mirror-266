""""
In this module, you can find various tools to create a scene. The scene must be eventually passed to `Renderer.bind_scene()` to be rendered.
Currently available scene tools are:
1. Scene:
2. Plane:
3. Disk:
4. Texture:
5. Camera:
"""

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from typing import List, Tuple, Union

DTYPE = np.float32


def normalize(v):
    return v / np.linalg.norm(v)


class InvalidTransformationMatrixError(Exception):
    def __init__(self, tmat):
        super(InvalidTransformationMatrixError, self).__init__(
            "The matrix is not a valid transformation. make sure to input a 4x4 premultiplying rigid transformation matrix."
        )


class Scene(QObject):
    """
    This is the scene object which contains all the components in a scene (e.g. plane, disk, etc.),
    The scene should be passed to `Renderer` to be rendered.
    """

    SceneModifiedEvent = pyqtSignal(object)  # whenever anything changes in the scene, this signal will be emitted.

    def __init__(
        self,
        actors: List["ModelBase"] = [],
        cameras: List["Camera"] = [],
    ):
        """
        args:
            actors: list of actors (e.g. planes, disks, etc).
            cameras: list of cameras.
        """
        super(Scene, self).__init__()
        self.actors = []
        self.cameras = []
        self.add_actors(actors)
        self.add_cameras(cameras)

    def add_actors(self, actors: List["ModelBase"]):
        """
        adds new actors to the self.actors list.
        args:
            actors: list of actors to be added.
        """
        if not isinstance(actors, list):
            actors = [actors]
        for act in actors:
            self.actors.append(act)
            act.ModelModifiedEvent.connect(self._actor_modified_event_handler)

    def add_cameras(self, cameras: List["Camera"]):
        """
        adds new cameras to the self.actors list.
        args:
            cameras: list of cameras to be added.
        """
        if not isinstance(cameras, list):
            cameras = [cameras]
        for cam in cameras:
            self.cameras.append(cam)
            cam.CameraModifiedEvent.connect(self._camera_modified_event_handler)

    def _actor_modified_event_handler(self, act: "ModelBase"):
        self.SceneModifiedEvent.emit(self)

    def _camera_modified_event_handler(self, cam: "Camera"):
        self.SceneModifiedEvent.emit(self)

    def copy(self):
        """
        creates a copy of the scene.
        """
        return self.duplicate(self)

    @classmethod
    def duplicate(cls, scene: "Scene"):
        """
        creates a duplicate of the input scene.
        """
        actors = [act.copy() for act in scene.actors]
        cameras = [cam.copy() for cam in scene.cameras]
        return cls(actors, cameras)


class ModelBase(QObject):
    """
    This class is the base class for representing an actor (a 3D object like a sphere) in the scene.
    """

    ModelModifiedEvent = pyqtSignal(object)  # any changes to the actor causes this signal to be emitted. `args: (actor)`.
    opacity = 1.0
    visible = True
    wire_frame = False  # enables or disable wireframe mode for rendering.
    selectable = True  # determines whether the actor can be clicked on or not (with the mouse).
    moveable = True  # determines wether an actor can be moved by mouse dragging or not
    color = np.array([255, 0, 0]).astype(np.uint8)
    texture_blend_fac = (
        0.0  # specifies the proportion of how much of texture and color should be blended to form actor's appearance.
    )
    line_width = 1.0  # line width of the actor when being rendered in wireframe mode or in outline mode.
    outline_mode = False  # enables or disable out_line mode for rendering.

    def __init__(self, name: str = ""):
        """
        Args:
            name: name of the actor (arbitrary name).
        """
        super(ModelBase, self).__init__()
        self.name = name
        self.mesh = None  # turns into Nx8 ndarray later.
        self.texture = None  # Pytorch3dMesh has the same attribute, please don't rename this attribute.
        self._tmat = np.eye(4)  # 4x4 premultiplying transformation matrix. this will be passed to opengl as model matrix.

    @property
    def nvertices(self):
        """
        return how many vertices the mesh consists of
        """
        if self.mesh is not None:
            return self.mesh.shape[0]
        else:
            return 0

    def get_model_matrix(self) -> np.ndarray:
        """
        model matrix to transform anatomy from object coordinates to world coordinates.
        Returns:
            4x4 premultiplying transformation matrix for use with OpenGL
        """
        return self._tmat

    def set_model_matrix(self, tmat: np.ndarray, emit_event=True):
        """
        sets model matrix for the actor.
        args:
            tmat: new 4x4 premultiplying rigid transformation matrix for use with OpenGL. the existing model matrix will be replaced with this one.
            emit_event: enables or disables emitting a pyqtsignal after setting the new model matrix.
        """
        # some checks to confirm the validity of the transformation matrix
        is_tmat_valid = True
        is_tmat_valid *= np.isclose(np.linalg.det(tmat), 1.0)
        is_tmat_valid *= tmat.ndim == 2
        is_tmat_valid *= tmat.shape[0] == 4
        is_tmat_valid *= tmat.shape[1] == 4
        is_tmat_valid *= tmat[3, 0] == 0
        is_tmat_valid *= tmat[3, 1] == 0
        is_tmat_valid *= tmat[3, 2] == 0
        is_tmat_valid *= tmat[3, 3] == 1
        if not is_tmat_valid:
            raise InvalidTransformationMatrixError(tmat)
        self._tmat = tmat
        if emit_event:
            self.ModelModifiedEvent.emit(self)

    def apply_new_model_matrix(
        self,
        newtmat,
        do_around_com=False,
        emit_event=True,
    ):
        """
        applies a new transform matrix (4x4) to the existing transform matrix.
        args:
            newtmat: new (4x4) premultiplying transformation matrix.
            do_around_com: apply the transformation on the zero-centered 3D model. If it's True, then the function applies the rotations around center of mass (com).
            emit_event: enables or disables emitting a pyqtsignal after applying the new model matrix.
        """
        comtmat = np.eye(4)
        if do_around_com:
            comtmat[0:3, 3] = self.get_mesh_center()
        newtmat = comtmat @ newtmat @ np.linalg.inv(comtmat)
        finaltmat = newtmat @ self.get_model_matrix()
        self.set_model_matrix(finaltmat, emit_event)

    def get_mesh_center(self) -> np.ndarray:
        """
        returns center of mass (com) of the mesh (considering model matrix).
        """
        com = np.ones((4,))
        com[0:3] = np.average(self.mesh[:, 0:3], axis=0)
        com = self.get_model_matrix() @ com
        return com[0:3]

    def set_color(self, r: int, g: int, b: int):
        """
        sets actor's color.
        args:
            r: red color between 0 to 255.
            g: green color between 0 to 255.
            b: blue color between 0 to 255.
        """
        self.color = np.array([r, g, b]).astype(np.uint8)
        self.ModelModifiedEvent.emit(self)

    def set_visible(self, visibility: bool):
        """
        sets actor's visibility.
        args:
            visibility: True or False.
        """
        self.visible = visibility
        self.ModelModifiedEvent.emit(self)

    def set_opacity(self, alpha: float):
        """
        sets actor's opacity.
        args:
            opacity: float between 0 and 1.
        """
        self.opacity = alpha
        self.ModelModifiedEvent.emit(self)

    def copy(self):
        return self._duplicate(self)

    @classmethod
    def _duplicate(cls, actor: "ModelBase"):
        act = cls.__new__(cls)
        ModelBase.__init__(act, actor.name + "_copy")
        act.mesh = actor.mesh  # don't use `copy()` mesh because it will cause memory issues.
        act.color = actor.color.copy()
        try:
            act.texture = actor.texture.copy()
        except AttributeError:
            act.texture = None
        act._tmat = actor._tmat.copy()
        act.visible = actor.visible
        act.opacity = actor.opacity
        return act

    def __repr__(self):
        return self.name


class Plane(ModelBase):
    """
    Use this class to create a plane in the scene.
    """

    texture_blend_fac = 1.0
    moveable = False

    def __init__(
        self,
        name: str,
        center_pos=(0.0, 0.0, 0.0),
        normal_vec=(0.0, 0.0, 1.0),
        vertical_vec=(0.0, 1.0, 0.0),
        width=400,
        height=400,
        texture=None,
    ):
        """
        Args:
            name: name of the plane.
            center_pos: center of plane plane in 3D space.).
            normal_vec: plane's normal vector.
            vertical_vec: plane's vertical vector.
            width: plane plane width, in milimeters.
            height: plane plane height, in milimeters.
            texture: texture to be projected on the plane.
        """
        super(Plane, self).__init__(name)
        self.center_pos = np.array(center_pos)
        self.normal_vec = normalize(np.array(normal_vec))
        self.vertical_vec = normalize(np.array(vertical_vec))
        self.width = width
        self.height = height
        self.texture = Texture() if texture is None else texture
        self.mesh = self.create_mesh(self.width, self.height)
        self._tmat = self.calculate_tmat(
            self.center_pos,
            self.normal_vec,
            self.vertical_vec,
        )

        self.set_color(245, 245, 245)

    @staticmethod
    def create_mesh(width: float, height: float) -> np.array:
        """
        creates mesh data for the plane (2 triangles and their texture coordinates). the mesh is actually a rectangle in xy plane.
        Args:
             width: width of the image plane in mm.
             height: height of the image plane in mm.
        Returns:
             np.array: 6*8, 2 triangles with 3 coordinates, 2 texture coordinates, 3 normals.
        """
        left = -width / 2.0
        right = -left
        bot = -height / 2.0
        top = -bot
        # 3 coords, 2 texture coords, 3 normals
        # as OpenGL uses different coordinate axes from most image libraries, we need to flip the texture
        plane = np.array(
            [
                [
                    left,
                    bot,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    1.0,
                ],
                [
                    right,
                    bot,
                    0.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    1.0,
                ],
                [
                    right,
                    top,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                ],
                [
                    right,
                    top,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                ],
                [
                    left,
                    top,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                ],
                [
                    left,
                    bot,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    1.0,
                ],
            ],
            dtype=DTYPE,
        )
        return plane

    @staticmethod
    def calculate_tmat(center_pos, normal_vec, vertical_vec):
        """
        calculates plane's model matrix to transform plane from object coordinates to world coordinates.
        Args:
            center_pos: center of plane plane; NOT image midpoint.
            normal_vec: plane's normal vector.
            vertical_vec: plane's vertical vector.
        Returns:
            4x4 premultiplying transformation matrix for use with OpenGL.
        """
        tmat = np.eye(4)
        up = normalize(vertical_vec)
        zaxis = normalize(normal_vec)
        xaxis = normalize(np.cross(up, zaxis))
        yaxis = np.cross(zaxis, xaxis)
        tmat[0, 0:3] = xaxis
        tmat[1, 0:3] = yaxis
        tmat[2, 0:3] = zaxis
        tmat = tmat.transpose()
        tmat[0:3, 3] = center_pos
        return tmat

    def copy(self):
        act = super(Plane, self).copy()
        act.center_pos = self.center_pos.copy()
        act.normal_vec = self.normal_vec.copy()
        act.vertical_vec = self.vertical_vec.copy()
        act.width = self.width
        act.height = self.height
        return act


class Disk(ModelBase):
    """
    a class to create a simple disk in the scene.
    """

    line_width = 1.0
    wire_frame = False
    outline_mode = False

    def __init__(self, name, diameter=50.0, nfrags=100):
        """
        args:
            name: name of the actor.
            diameter: diameter of the disk in milimeters.
            nfrags: number of fragments that the disk will be created from.
        """
        super(Disk, self).__init__(name)
        self._diameter = diameter
        self.mesh = self.create_mesh(diameter / 2, nfrags)

    @staticmethod
    def create_mesh(radius, nfrags):
        mesh = np.zeros((3 * nfrags, 8), dtype=DTYPE)
        t = np.linspace(0, 2 * np.pi, nfrags + 1)
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        for i in range(nfrags):
            o1 = np.array([0, 0, 0])
            a1 = np.array([x[i], y[i], 0])
            b1 = np.array([x[i + 1], y[i + 1], 0])

            mesh[3 * i + 0, 0:3] = o1
            mesh[3 * i + 1, 0:3] = a1
            mesh[3 * i + 2, 0:3] = b1
            mesh[3 * i + 0, 5:8] = [0.0, 0.0, 1.0]
            mesh[3 * i + 1, 5:8] = [0.0, 0.0, 1.0]
            mesh[3 * i + 2, 5:8] = [0.0, 0.0, 1.0]

        return mesh

    def copy(self):
        act = super(Disk, self).copy()
        act._diameter = self.diameter
        return act

    @property
    def diameter(self):
        return self._diameter

    @classmethod
    def fit_to_points(cls, points_array, name, nfrags=50):
        # points_array should be a nx2 numpy array
        # method from https://lucidar.me/en/mathematics/least-squares-fitting-of-circle/
        npoints = points_array.shape[0]
        A = np.concatenate(
            (points_array, np.ones((npoints, 1))),
            axis=-1,
        )
        B = np.sum(points_array**2, axis=1).reshape(-1, 1)
        X = np.linalg.inv(A.T @ A) @ A.T @ B
        X = X.flatten()
        xc = X[0] / 2
        yc = X[1] / 2
        r = np.sqrt(4 * X[2] + X[0] ** 2 + X[1] ** 2) / 2
        disk = cls(name, 2 * r, nfrags)
        disk.apply_new_model_matrix(
            np.array(
                [
                    [1.0, 0.0, 0.0, xc],
                    [0.0, 1.0, 0.0, yc],
                    [0.0, 0.0, 1.0, 0.1],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
        )
        disk.wire_frame = False
        disk.outline_mode = True
        disk.selectable = False
        disk.moveable = False
        disk.set_color(255, 51, 153)
        disk.line_width = 3
        return disk


class Texture(object):
    """
    use this class to store an image as a texture to project it on an actor (e.g. a plane).
    """

    def __init__(
        self,
        img_array: np.ndarray,
        pixel_size=1.0,
    ):
        """
        args:
            img_array: 2D (grayscale) or 3D (RGB) array of image.
            pixel_size: size of each pixel in milimeters. size along x and y is assumed to be equal.
        """
        self.pixel_size = pixel_size
        self.img = img_array.copy()

    @staticmethod
    def change_aspect_ratio_with_padding(img, wh):
        """

        :param img:
        :param wh: w/h value
        :return:
        """
        current_wh = img.shape[1] / img.shape[0]
        if current_wh > wh:
            w0 = 0
            h0 = img.shape[1] / wh - img.shape[0]
        elif current_wh < wh:
            w0 = img.shape[0] * wh - img.shape[1]
            h0 = 0
        else:
            return img
        w0 = int(w0 / 2)
        h0 = int(h0 / 2)
        im = np.pad(
            img,
            ((h0, h0), (w0, w0)),
            constant_values=0,
        )
        return im

    @property
    def width(self):
        """
        returns image's width in milimeters.
        """
        return self.pixel_size * self.img.shape[1]

    @property
    def height(self):
        """
        returns image's height in milimeters.
        """
        return self.pixel_size * self.img.shape[0]

    def copy(self):
        return self._duplicate(self)

    @classmethod
    def _duplicate(cls, tex: "Texture"):
        newtex = cls(tex.img.copy(), tex.pixel_size)
        return newtex


class Camera(QObject):
    """
    use this class to define a camera in the scene. the renderer needs the camera to render the scene.
    """

    CameraModifiedEvent = pyqtSignal(object)  # any changes to the actor causes this signal to be emitted. `args: (camera)`.

    def __init__(
        self,
        name: str = "",
        screen_world_pos: np.ndarray = np.array([0, 0, 0]),
        screen_normal: np.ndarray = np.array([0, 0, 1]),
        screen_vert: np.ndarray = np.array([0, 1, 0]),
        screen_size_width: float = 1000,
        screen_size_height: float = 1000,
        principal_point_h: float = 0,
        principal_point_v: float = 0,
        focal_length: float = 1000,
    ):
        """
        Args:
            screen_world_pos: the 3 world coordinates of the screen's midpoint.
            screen_normal: the direction of the screen's normal.
            screen_vert: the screen's vertical direction.
            screen_size_width, screen_size_height: width and height of the screen, in milimeters.
            principal_point_h, principal_point_v: horizontal and vertical principal points given
                in the image coordinate system (in respect to the image midpoint; not plane midpoint), obtained by SI calibration procedure.
            focal_length: perpendicular distance (milimeters) from camera to the screen. enter as positive number.
        ..Note:: the projection details such as FOV or clippling planes are set by `self.default_proj_mat4()`
        """
        super(Camera, self).__init__()
        self.name = name
        self.pph = principal_point_h
        self.ppv = principal_point_v
        self.focal_length = focal_length
        self.screen_world_pos = np.array(screen_world_pos)
        self.screen_normal = normalize(screen_normal)
        self.screen_vert = normalize(screen_vert)
        self.screen_size = [
            screen_size_width,
            screen_size_height,
        ]
        self._zoom = 1
        self._pan = [0, 0]

    def lookat_screen_mat4(self) -> np.array:
        """
        Creates view matrix (the camera up-direction is hardcoded as screen bot->top)
        Variation of gluLookAt, but with respect to the calibration data we are collecting
        Returns:
            a 4x4 matrix suitable to be passed as veiw matrix to an OpenGL vertex shader.
        """
        # dont look at the center of the screen but at the principal point
        # first fake camera position by translating everything in the other direction
        translation = np.eye(4)
        translation[0:3, 3] = -self.get_cam_pos()
        # then rotate to new axes (remember that -z goes into the screen)
        xaxis, yaxis, zaxis = self.corrected_camera_axes
        rot = np.eye(4)
        rot[0, 0:3] = xaxis
        rot[1, 0:3] = yaxis
        rot[2, 0:3] = zaxis
        view_matrix = rot @ translation
        return view_matrix

    def get_cam_pos(self):
        """
        returns position of the camera.
        """
        # set z coordinate so that the distance along z between screen and eye is exactly the focal length
        z = np.abs(self.focal_length) * self.corrected_camera_axes[2]
        cam_pos = self.get_cam_target() + z
        return cam_pos

    def get_cam_target(self):
        """
        returns camera's target which is the prinvipal point in global coordinate system.
        """
        h = self.pph * self.corrected_camera_axes[0]
        v = self.ppv * self.corrected_camera_axes[1]
        target = self.screen_world_pos + h + v
        return target

    @staticmethod
    def compute_ortho_matrix(left, right, bot, top, near, far):
        """
        docs.gl/gl3/glOrtho
        Args:
            left, right, bot, top, near, far: clipping planes.
            near, far: both positive
        """
        m = np.zeros((4, 4), dtype=DTYPE)
        m[0, 0] = 2 / (right - left)
        m[0, 3] = -(right + left) / (right - left)
        m[1, 1] = 2 / (top - bot)
        m[1, 3] = -(top + bot) / (top - bot)
        m[2, 2] = -2 / (far - near)
        m[2, 3] = -(far + near) / (far - near)
        m[3, 3] = 1.0
        return m

    @staticmethod
    def compute_perspective_matrix(left, right, bot, top, near, far):
        """
        docs.gl/gl3/glFrustum
        Args:
            left, right, bot, top, near, far: clipping planes.
            near, far: both positive
        """
        m = np.zeros((4, 4), dtype=DTYPE)
        m[0, 0] = 2 * near / (right - left)
        m[0, 2] = (right + left) / (right - left)
        m[1, 1] = 2 * near / (top - bot)
        m[1, 2] = (top + bot) / (top - bot)
        m[2, 2] = -(far + near) / (far - near)
        m[2, 3] = -2 * far * near / (far - near)
        m[3, 2] = -1.0
        return m

    def default_proj_mat4(self):
        """
        projection matrix to see the full screen_size
        Args:
        Returns:
            4x4 projection matrix to be used as orthogonal/perspective matrix in opengl vertex shader.
        """
        # proj = self.compute_ortho_matrix(self.left, self.right, self.bot, self.top, self.near, self.far)
        proj = self.compute_perspective_matrix(self.left, self.right, self.bot, self.top, self.near, self.far)
        return proj

    def screen2world(self, xs, ys, width, height):
        """
        converts screen coordinates (xs, ys) to world coordinates (xw, yw, zw).
        args:
            xs: x coordinate of viewport pixel.
            ys: y coordinate of viewport pixel
            width: width of viewport (number of pixels)
            height: height of viewport (number of pixels)
        """
        xsn = (xs - 1) * 2 / (width - 1) - 1
        ysn = (ys - 1) * 2 / (height - 1) - 1
        zsn = (self.focal_length - self.near) * 2 / (self.far - self.near) - 1
        # zsn = -1  # at near plane
        world_pos = np.linalg.inv(self.default_proj_mat4() @ self.lookat_screen_mat4()) @ np.array([xsn, ysn, zsn, 1.0])
        world_pos = world_pos.flatten()
        world_pos = world_pos / world_pos[-1]

        return np.array(world_pos[0:3])

    @property
    def near(self):
        return self.focal_length / 8

    @property
    def far(self):
        return self.focal_length * 4

    @property
    def right(self):
        screen_width = self.screen_size[0]
        return screen_width / self.zoom / 2 + self.pan[0]

    @property
    def left(self):
        screen_width = self.screen_size[0]
        return -screen_width / self.zoom / 2 + self.pan[0]

    @property
    def top(self):
        screen_height = self.screen_size[1]
        return screen_height / self.zoom / 2 + self.pan[1]

    @property
    def bot(self):
        screen_height = self.screen_size[1]
        return -screen_height / self.zoom / 2 + self.pan[1]

    @property
    def zoom(self):
        return self._zoom

    @property
    def pan(self):
        return self._pan

    @zoom.setter
    def zoom(self, val):
        self._zoom = max(val, 1)
        self.CameraModifiedEvent.emit(self)

    @pan.setter
    def pan(self, xy):
        self._pan = xy
        self.CameraModifiedEvent.emit(self)

    @property
    def corrected_camera_axes(self):
        """
        normally, there is no guarantee that the vectors given by user are perpendicular. so we use this function
        to get a perpendicular form of those vectors.
        """
        up = normalize(self.screen_vert)
        zaxis = normalize(self.screen_normal)
        xaxis = normalize(np.cross(up, zaxis))
        yaxis = np.cross(zaxis, xaxis)
        return xaxis, yaxis, zaxis

    def copy(self):
        return self._duplicate(self)

    @classmethod
    def _duplicate(cls, camera: "Camera"):
        cam = cls(
            camera.name + "_copy",
            camera.screen_world_pos,
            camera.screen_normal,
            camera.screen_vert,
            camera.screen_size[0],
            camera.screen_size[1],
            camera.pph,
            camera.ppv,
            camera.focal_length,
        )
        cam._zoom = camera._zoom
        cam._pan = camera._pan
        return cam


if __name__ == "__main__":
    pass
