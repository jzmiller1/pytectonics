from numpy import array, asarray, sqrt, dot, cos, sin, cross


def mag(v):
    return sqrt(dot(v, v))


class MyFrame:
    """Reimplmenting most of what vPython did with the frame...

    https://github.com/vpython/visual/blob/e856d1b89d8ab0484409f4be7931326ed546e9a2/src/core/frame.cpp

    """

    def __init__(self):
        self.axis = array([1, 0, 0])
        self.pos = array([0, 0, 0])
        self.up = array([0, 1, 0])

    def frame_to_world(self, a):
        """ this is being used on line 150, in getCartesian so it needs to
        be implemented

        """
        return array([0, 0, 0])

    def world_zaxis(self):
        if dot(self.axis, self.up) / sqrt(mag(self.up) * mag(self.axis)) > 0.98:
            if dot(mag(self.axis), array([-1, 0, 0])) > 0.98:
                z = mag(cross(self.axis, array([0, 0, 1])))
            else:
                z = mag(cross(self.axis, array([-1, 0, 0])))
        else:
            z = mag(cross(self.axis, self.up))
        return z

    def world_to_frame(self, a):
        z = array([0, 0, self.world_zaxis()])
        part = cross(z, self.axis)
        y = part / sqrt(dot(part, part))
        x = self.axis / sqrt(dot(self.axis, self.axis))
        v = a - self.pos
        return dot(v, x), dot(v, y), dot(v, z)

    def rotate(self, *args, **kwargs):
        def rotation_matrix(axis, theta):
            """
            Return the rotation matrix associated with counterclockwise rotation
            about the given axis by theta radians.

            From:
            https://stackoverflow.com/questions/6802577/rotation-of-3d-vector

            """
            axis = asarray(axis)
            axis = axis / sqrt(dot(axis, axis))
            a = cos(theta / 2.0)
            b, c, d = -axis * sin(theta / 2.0)
            aa, bb, cc, dd = a * a, b * b, c * c, d * d
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            return array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                          [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                          [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

        rotated = dot(rotation_matrix(kwargs['axis'],
                                      kwargs['angle']),
                      self.axis)
        self.axis = rotated
