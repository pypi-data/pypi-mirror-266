""" reinventing the wheel: small transform library """
import numpy as np

class Quaternion(object):
    def __init__(self, x, y, z, w):
        self._x = x
        self._y = y
        self._z = z
        self._w = w

    def __repr__(self):
        return "Quaternion(x={:.9f}, y={:.9f}, z={:.9f}, w={:.9f})".format(*self.xyzw())

    def as_quaternion(something):
        if isinstance(something, Quaternion):
            return something
        elif isinstance(something, tuple) and len(something) == 4:
            return Quaternion(*something)
        elif isinstance(something, list) and len(something) == 4:
            return Quaternion(*something)
        else:
            raise ValueError("Cannot convert {} to Quaternion".format(something))
    
    def xyzw(self):
        return [self._x, self._y, self._z, self._w]

    def from_transform_matrix(self, matrix4x4):
        x, y, z, w = quaternion_from_transform_matrix(matrix4x4)
        return Quaternion(x, y, z, w)

    def to_transform_matrix(self):
        return transform_matrix_from_quaternion(*self.xyzw())

class Transform(object):
    def __init__(self, origin=None, x_axis=None, y_axis=None, quaternion=None):
        self._matrix = None
        self._quaternion = None
        if x_axis is not None or y_axis is not None:
            if x_axis is None or y_axis is None:
                raise ValueError("Underspecified transform: Must specify neither or both axes.")
        if origin is not None or x_axis is not None or y_axis is not None:
            self._matrix = np.eye(4)
            if x_axis is not None and y_axis is not None:
                if quaternion is not None:
                    raise ValueError("Overspecified transform: Cannot specify both quaternion and axes")
                self._matrix[:3, 0] = x_axis
                self._matrix[:3, 1] = y_axis
                self._matrix[:3, 2] = np.cross(x_axis, y_axis)
            if origin is not None:
                self._matrix[:3, 3] = origin
        if quaternion is not None:
            self._quaternion = Quaternion.as_quaternion(quaternion)

    def to_json_dict(self):
        json_dict = {
            "type": "Transform",
            "_matrix": self._matrix.tolist() if self._matrix is not None else None,
            "_quaternion": self._quaternion.xyzw() if self._quaternion is not None else None,
        }
        return json_dict
    
    def from_json_dict(json_dict):
        new = Transform()
        new._matrix = np.array(json_dict["_matrix"]) if json_dict["_matrix"] is not None else None
        new._quaternion = Quaternion(*json_dict["_quaternion"]) if json_dict["_quaternion"] is not None else None
        return new

    def __repr__(self):
        return "Transform(origin={}, x_axis={}, y_axis={})".format(self.origin(), self.x_axis(), self.y_axis())

    def __mul__(self, other):
        """ T_A_in_B * T_B_in_C = T_A_in_C """
        if isinstance(other, Transform):
            return Transform.from_matrix(np.dot(other.matrix(), self.matrix()))
        else:
            raise NotImplementedError
        
    def is_right_handed(self):
        return np.linalg.det(self.matrix()[:3, :3]) > 0
        
    def from_matrix(matrix4x4):
        new = Transform()
        new._matrix = matrix4x4
        return new

    def from_quaternion(quaternion, origin=None):
        return Transform(origin=origin, quaternion=quaternion)
    
    def from_axis_angle(axis, angle_rad, translation=None):
        """ translation is not the axis origin! To implement rotation around an origin, use from_rotation_around_point """
        new = Transform()
        new._matrix = transform_matrix_from_axis_angle(axis, angle_rad, translation)
        return new

    def from_rotation_around_point(axis, angle_rad, point):
        new = Transform()
        new._matrix = transform_matrix_from_axis_angle(axis, angle_rad)
        # to get translation, rotate point around axis at origin, compare to previous
        rotated_point = new.transform_points([point])[0]
        new._matrix[:3, 3] = point - rotated_point
        return new

    def inverse(self):
        return Transform.from_matrix(inverse(self.matrix()))
    
    def matrix(self):
        if self._quaternion is not None:
            rot_mat4x4 = self.quaternion().to_transform_matrix()
            if self._matrix is not None:
                if not np.allclose(self._matrix[:3, :3], np.eye(3)):
                    raise ValueError("Overdefined transform: transform has a non-zero quaternion and non-zero rotation matrix.")
                rot_mat4x4[:3, 3] = self._matrix[:3, 3]
            return rot_mat4x4
        elif self._matrix is not None:
            return self._matrix
        else:
            return np.eye(4)

    def quaternion(self):
        if self._quaternion is not None:
            return self._quaternion
        elif self._matrix is not None:
            return Quaternion(*quaternion_from_transform_matrix(self.matrix()))
        else:
            return Quaternion(0, 0, 0, 1)

    def origin(self):
        return self.matrix()[:3, 3]

    def translation(self):
        return self.origin()

    def x_axis(self):
        return self.matrix()[:3, 0]

    def y_axis(self):
        return self.matrix()[:3, 1]

    def z_axis(self):
        return self.matrix()[:3, 2]

    def to_axis_angle(self):
        return axis_angle_from_transform_matrix(self.matrix())

    def to_compas_frame(self):
        from compas.geometry import Frame
        return Frame(self.origin(), self.x_axis(), self.y_axis())

    def from_compas_frame(frame):
        return Transform([frame.point.x, frame.point.y, frame.point.z], frame.xaxis, frame.yaxis)

    def to_pose_msg(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        x, y, z = self.origin()
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z
        qx, qy, qz, qw = self.quaternion().xyzw()
        pose.orientation.x = qx
        pose.orientation.y = qy
        pose.orientation.z = qz
        pose.orientation.w = qw
        return pose
    
    def from_pose_msg(pose_msg):
        x = pose_msg.position.x
        y = pose_msg.position.y
        z = pose_msg.position.z
        qx = pose_msg.orientation.x
        qy = pose_msg.orientation.y
        qz = pose_msg.orientation.z
        qw = pose_msg.orientation.w
        return Transform.from_quaternion(Quaternion(qx, qy, qz, qw), [x, y, z])
    
    def transform_vector(self, vector_in_A_frame):
        """ If this transform is the transform of A in B, then this returns the vector in B frame """
        return transform_vector(vector_in_A_frame, self.matrix())
    
    def transform_point(self, point):
        return transform_point(point, self.matrix())

    def transform_points(self, points):
        return transform_points(points, self.matrix())
    
    def plot_polyscope(self, name="A_in_B", axis_length=0.1):
        show_frame_in_polyscope(self.matrix(), name=name, axis_length=axis_length)

    def print_matrix(self):
        # 1 decimal
        for row in self.matrix():
            for val in row:
                print("{:.1f}".format(val), end=" ")
            print()


def inverse(transform_matrix_A_in_B):
    transform_matrix_B_in_A = np.linalg.inv(transform_matrix_A_in_B)
    return transform_matrix_B_in_A


def show_frame_in_polyscope(frame_in_world_matrix, name="frame", axis_length=1.0):
    import polyscope as ps
    origin = frame_in_world_matrix[:3, 3]
    x_axis = frame_in_world_matrix[:3, 0]
    y_axis = frame_in_world_matrix[:3, 1]
    z_axis = frame_in_world_matrix[:3, 2]
    ps.register_curve_network(
        "{}_x_axis".format(name),
        np.array([origin, origin + x_axis * axis_length]),
        np.array([[0, 1]]),
        color=(1.0, 0.0, 0.0),
    )
    ps.register_curve_network(
        "{}_y_axis".format(name),
        np.array([origin, origin + y_axis * axis_length]),
        np.array([[0, 1]]),
        color=(0.0, 1.0, 0.0),
    )
    ps.register_curve_network(
        "{}_z_axis".format(name),
        np.array([origin, origin + z_axis * axis_length]),
        np.array([[0, 1]]),
        color=(0.0, 0.0, 1.0),
    )


def transform_matrix_from_origin_and_xy_axes(origin, x_axis, y_axis):
    """
    returns the matrix for the transform A in B, where origin is the origin of A in B, and x_axis and y_axis are the x and y axes of A in B
    """
    z_axis = np.cross(x_axis, y_axis)
    xx, xy, xz = x_axis
    yx, yy, yz = y_axis
    zx, zy, zz = z_axis
    ox, oy, oz = origin
    transform_matrix = np.array(
        [
            [xx, yx, zx, ox],
            [xy, yy, zy, oy],
            [xz, yz, zz, oz],
            [0, 0, 0, 1],
        ]
    )
    return transform_matrix

def transform_matrix_from_translation(translation):
    transform_matrix = transform_matrix_from_origin_and_xy_axes(translation, [1, 0, 0], [0, 1, 0])
    return transform_matrix

def transform_matrix_from_axis_angle(axis, angle, translation=None):
    """ angle in radians """
    ux, uy, uz = axis
    tx, ty, tz = translation if translation is not None else [0, 0, 0]
    transform_matrix = np.array(
        [
            [ux * ux * (1 - np.cos(angle)) + np.cos(angle), ux * uy * (1 - np.cos(angle)) - uz * np.sin(angle), ux * uz * (1 - np.cos(angle)) + uy * np.sin(angle), tx],
            [uy * ux * (1 - np.cos(angle)) + uz * np.sin(angle), uy * uy * (1 - np.cos(angle)) + np.cos(angle), uy * uz * (1 - np.cos(angle)) - ux * np.sin(angle), ty],
            [uz * ux * (1 - np.cos(angle)) - uy * np.sin(angle), uz * uy * (1 - np.cos(angle)) + ux * np.sin(angle), uz * uz * (1 - np.cos(angle)) + np.cos(angle), tz],
            [0, 0, 0, 1],
        ]
    )
    return transform_matrix

def axis_angle_from_transform_matrix(transform_matrix):
    """ returns axis, angle """
    R = transform_matrix[:3, :3]
    angle = np.arccos((np.trace(R) - 1) / 2)
    if angle == 0:
        return None, 0
    if np.allclose(angle, np.pi):
        pass
    axis = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(angle))
    norm = np.linalg.norm(axis)
    if norm != 0:
        axis = axis / norm
    return axis, angle

def axis_angle_from_transform_matrix(transform_matrix):
    """ returns axis, angle 
    https://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToAngle/
    """
    R = transform_matrix[:3, :3]
    epsilon = 0.0001 # margin to allow for rounding errors
    epsilon2 = 0.1 # margin to distinguish between 0 and 180 degrees
    if ((np.abs(R[0, 1]-R[1, 0])< epsilon)      and (np.abs(R[0, 2]-R[2, 0])< epsilon)      and (np.abs(R[1, 2]-R[2, 1])< epsilon)) :
        # singularity found
        # first check for identity matrix which must have +1 for all terms
        #  in leading diagonaland zero in other terms
        if ((np.abs(R[0, 1]+R[1, 0]) < epsilon2) and (np.abs(R[0, 2]+R[2, 0]) < epsilon2) and (np.abs(R[1, 2]+R[2, 1]) < epsilon2) and (np.abs(R[0, 0]+R[1, 1]+R[2, 2]-3) < epsilon2)) :
            # this singularity is identity matrix so angle = 0
            return None, 0 # zero angle, arbitrary axis
        
        # otherwise this singularity is angle = 180
        angle = np.pi
        xx = (R[0, 0]+1)/2
        yy = (R[1, 1]+1)/2
        zz = (R[2, 2]+1)/2
        xy = (R[0, 1]+R[1, 0])/4
        xz = (R[0, 2]+R[2, 0])/4
        yz = (R[1, 2]+R[2, 1])/4
        if ((xx > yy) and (xx > zz)) : # R[0, 0] is the largest diagonal term
            if (xx< epsilon) :
                x = 0
                y = 0.7071
                z = 0.7071
            else :
                x = np.sqrt(xx)
                y = xy/x
                z = xz/x
            
        elif (yy > zz) : # R[1, 1] is the largest diagonal term
            if (yy< epsilon) :
                x = 0.7071
                y = 0
                z = 0.7071
            else :
                y = np.sqrt(yy)
                x = xy/y
                z = yz/y
                
        else : # R[2, 2] is the largest diagonal term so base result on this
            if (zz< epsilon) :
                x = 0.7071
                y = 0.7071
                z = 0
            else :
                z = np.sqrt(zz)
                x = xz/z
                y = yz/z
            
        return np.array([x, y, z]), angle # return 180 deg rotation
    
    # as we have reached here there are no singularities so we can handle normally
    s = np.sqrt((R[2, 1] - R[1, 2])*(R[2, 1] - R[1, 2])
        +(R[0, 2] - R[2, 0])*(R[0, 2] - R[2, 0])
        +(R[1, 0] - R[0, 1])*(R[1, 0] - R[0, 1])) # used to normalise
    if (np.abs(s) < 0.001):
        s=1 
        # prevent divide by zero, should not happen if matrix is orthogonal and should be
        # caught by singularity test above, but I've left it in just in case
    angle = np.arccos(( R[0, 0] + R[1, 1] + R[2, 2] - 1)/2)
    x = (R[2, 1] - R[1, 2])/s
    y = (R[0, 2] - R[2, 0])/s
    z = (R[1, 0] - R[0, 1])/s
    return np.array([x, y, z]), angle

def transform_matrix_from_quaternion(x, y, z, w):
    transform_matrix = np.array([
        [1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w, 0],
        [2 * x * y + 2 * z * w, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * x * w, 0],
        [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x * x - 2 * y * y, 0],
        [0, 0, 0, 1],
    ])
    return transform_matrix

def quaternion_from_transform_matrix(transform_matrix):
    """ Returns x, y, z, w components of the quaternion defined by the upper left part of the 4x4 transform_matrix """
    q = np.empty((4, ), dtype=np.float64)
    M = np.array(transform_matrix, dtype=np.float64, copy=False)[:4, :4]
    t = np.trace(M)
    if t > M[3, 3]:
        q[3] = t
        q[2] = M[1, 0] - M[0, 1]
        q[1] = M[0, 2] - M[2, 0]
        q[0] = M[2, 1] - M[1, 2]
    else:
        i, j, k = 0, 1, 2
        if M[1, 1] > M[0, 0]:
            i, j, k = 1, 2, 0
        if M[2, 2] > M[i, i]:
            i, j, k = 2, 0, 1
        t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
        q[i] = t
        q[j] = M[i, j] + M[j, i]
        q[k] = M[k, i] + M[i, k]
        q[3] = M[k, j] - M[j, k]
    q *= 0.5 / np.sqrt(t * M[3, 3])
    x, y, z, w = q
    return x, y, z, w

def transform_points(points_in_A_frame, transform_matrix_A_in_B):
    points_in_A_frame = np.asanyarray(points_in_A_frame).reshape((-1, 3))
    transform_matrix_A_in_B = np.asanyarray(transform_matrix_A_in_B)
    _N, _3 = points_in_A_frame.shape
    _4, _4 = transform_matrix_A_in_B.shape
    # add a dimension to points_in_A_frame
    points_in_A_frame = np.hstack([points_in_A_frame, np.ones((_N, 1))])
    # transform_matrix_A_in_B
    points_in_B_frame = np.dot(points_in_A_frame, transform_matrix_A_in_B.T)
    # remove the dimension
    points_in_B_frame = points_in_B_frame[:, :-1]
    return points_in_B_frame

def transform_point(point_in_A_frame, transform_matrix_A_in_B):
    return transform_points(np.asanyarray(point_in_A_frame).reshape((1, 3)), transform_matrix_A_in_B).reshape((3,))

def transform_vectors(vectors_in_A_frame, transform_matrix_A_in_B):
    rotation_matrix_A_in_B = np.zeros_like(transform_matrix_A_in_B)
    rotation_matrix_A_in_B[:3, :3] = transform_matrix_A_in_B[:3, :3]
    return transform_points(vectors_in_A_frame, rotation_matrix_A_in_B)

def transform_vector(vector_in_A_frame, transform_matrix_A_in_B):
    return transform_vectors(vector_in_A_frame.reshape((1, 3)), transform_matrix_A_in_B).reshape((3,))

def transform_matrix_from_frame(frame):
    from compas.geometry.transformations import Transformation
    return np.array(Transformation.from_frame(frame).matrix)

def rotate_points_around_axis(points, axis_origin, axis, angle):
    translation_matrix = transform_matrix_from_translation(-np.array(axis_origin))
    rotation_matrix = transform_matrix_from_axis_angle(axis, angle)
    reverse_translation_matrix = transform_matrix_from_translation(np.array(axis_origin))
    return transform_points(points, reverse_translation_matrix @ rotation_matrix @ translation_matrix)

def test_transform_code(human=False):
    t = Transform([0, 0, 0], [1, 0, 0], [0, 1, 0])
    assert np.allclose(t.quaternion().xyzw(), [0, 0, 0, 1])
    assert np.allclose(t.matrix(), np.eye(4))
    if human:
        import polyscope as ps
        ps.init()
        ps.set_up_dir("z_up")
        show_frame_in_polyscope(np.eye(4), name="origin")
        tmat_test_in_origin_list = [
            transform_matrix_from_origin_and_xy_axes([1, 1, 1], [0, 1, 0], [-1, 0, 0]),
            transform_matrix_from_origin_and_xy_axes([1, -1, 1], [0, 0, 1], [1, 0, 0]),
            transform_matrix_from_origin_and_xy_axes(
                [-1, 1, 1], [np.cos(1.0), np.sin(1.0), 0], [-np.sin(1.0), np.cos(1.0), 0]
            ),
            transform_matrix_from_origin_and_xy_axes(
                [-1, -1, 1], [np.cos(1.0), 0, np.sin(1.0)], [0, 1, 0]
            ),
        ]
        for i, tmat_test_in_origin in enumerate(tmat_test_in_origin_list):
            show_frame_in_polyscope(tmat_test_in_origin, name="test_frame_{}".format(i))
            point_in_test = [0.5, 0.5, 0.5]
            point_in_o = transform_points(point_in_test, tmat_test_in_origin)
            print(point_in_test)
            ps.register_point_cloud(
                "point_{}".format(i), np.array(point_in_o).reshape((1, 3))
            )
        ps.show()

def point_2d_to_3d(point_2d, z=0):
    return np.array([point_2d[0], point_2d[1], z])

def points_2d_to_3d(points_2d, z=0):
    _N, _2 = points_2d.shape
    if _2 != 2:
        raise ValueError("points_2d must be Nx2")
    return np.hstack([np.asanyarray(points_2d), np.ones((len(points_2d), 1)) * z])

def test_axis_angle_roundtrip(human=False):
    for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        for angle in [np.pi / 3, np.pi / 2, np.pi]:
            tmat = transform_matrix_from_axis_angle(axis, angle)
            axis_out, angle_out = axis_angle_from_transform_matrix(tmat)
            assert np.allclose(axis, axis_out)
            assert np.allclose(angle, angle_out)

def test_axis_angle_180_deg(human=False):
    from schema.geometry import normalized
    for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1], normalized([1, 1, 1])]:
        for angle in [np.pi]:
            tmat = transform_matrix_from_axis_angle(axis, angle)
            t = Transform.from_matrix(tmat)
            axis_out, angle_out = t.to_axis_angle()
            assert np.allclose(axis, axis_out)
            assert np.allclose(angle, angle_out)
            if human:
                print(axis, angle, axis_out, angle_out)

def test_axis_angle_180deg_exact(human=False):
    # rotation by 180 deg around z trips up the algorithm
    cases = [
        {"x_axis": [-1,  0,  0], "y_axis": [ 0, -1,  0], "expected_axis": [0, 0, 1], "expected_angle": np.pi},
        {"x_axis": [-1,  0,  0], "y_axis": [ 0,  1,  0], "expected_axis": [0, 1, 0], "expected_angle": np.pi},
        {"x_axis": [ 1,  0,  0], "y_axis": [ 0, -1,  0], "expected_axis": [1, 0, 0], "expected_angle": np.pi},
        # 2-axis rotations
        {"x_axis": [ 0,  1,  0], "y_axis": [ 1,  0,  0], "expected_axis": [0.70710678, 0.70710678, 0.        ], "expected_angle": np.pi},
        {"x_axis": [-1,  0,  0], "y_axis": [ 0,  0,  1], "expected_axis": [0.        , 0.70710678, 0.70710678], "expected_angle": np.pi},
        {"x_axis": [ 0,  0,  1], "y_axis": [ 0, -1,  0], "expected_axis": [0.70710678, 0.        , 0.70710678], "expected_angle": np.pi},
        # 3-axis rotations
        {"x_axis": [ 0,  1,  0], "y_axis": [ 0,  0,  1], "expected_axis": [0.57735027, 0.57735027, 0.57735027], "expected_angle": 2.0943951023931957},
        {"x_axis": [ 0,  0,  1], "y_axis": [ 1,  0,  0], "expected_axis": [-0.57735027, -0.57735027, -0.57735027], "expected_angle": 2.0943951023931957},
    ]
    for case in cases:
        x_axis = case["x_axis"]
        y_axis = case["y_axis"]
        expected_angle = case["expected_angle"]
        expected_axis = case["expected_axis"]
        t = Transform([0, 0, 0], x_axis, y_axis)
        axis, angle = t.to_axis_angle()
        is_axis_error = not np.allclose(axis, expected_axis)
        is_angle_error = not np.allclose(angle, expected_angle)
        is_error = is_axis_error or is_angle_error
        if is_error:
            error_message = "x_axis: {}, y_axis: {}, expected: {}, got: {}".format(x_axis, y_axis, (expected_axis, expected_angle), (axis, angle))
            if human:
                print(error_message)
            raise ValueError(error_message)

def test_rotation_around_point(human=False):
    point = [0.5, 0.5, 0.5]
    axis = [0, 0, 1]
    angle = np.pi / 2
    object = [1, 0, 0]
    expected = [1, 1, 0]
    transform = Transform.from_rotation_around_point(axis, angle, point)
    result = transform.transform_point(object)
    assert np.allclose(result, expected), "expected: {}, got: {}".format(expected, result)

def test_json_roundtrip(human=False):
    transforms = [
        Transform([1, 2, 3], [1, 0, 0], [0, 1, 0]),
        Transform([1, 2, 3], quaternion=[0, 0, 0, 1]),
    ]
    for t in transforms:
        json_dict = t.to_json_dict()
        t2 = Transform.from_json_dict(json_dict)
        assert np.allclose(t.matrix(), t2.matrix())
        assert np.allclose(t.quaternion().xyzw(), t2.quaternion().xyzw())
        assert np.allclose(t.origin(), t2.origin())
        assert np.allclose(t.x_axis(), t2.x_axis())
        assert np.allclose(t.y_axis(), t2.y_axis())
        if human:
            print("Original:")
            t.print_matrix()
            print("After JSON roundtrip:")
            t2.print_matrix()

if __name__ == "__main__":
    HUMAN = True
    test_json_roundtrip(human=HUMAN)
    test_axis_angle_180deg_exact(human=HUMAN)
    test_axis_angle_180_deg(human=HUMAN)
    test_axis_angle_roundtrip(human=HUMAN)
    test_transform_code(human=HUMAN)
