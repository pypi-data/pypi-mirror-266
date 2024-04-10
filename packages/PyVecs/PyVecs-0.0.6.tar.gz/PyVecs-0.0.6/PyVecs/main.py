from math import sqrt, sin, cos, atan2, acos

def is_scalar(other):
    return type(other) in [int, float]

def is_vector2(other):
    return type(other) is Vector2

def is_vector3(other):
    return type(other) is Vector3

def angle_between_vectors(v, u) -> float:
    """
    return: angle between two vectors (2D or 3D) in rad.
    """
    dp = v.dot(u)

    if dp == 0:
        return 0

    return acos(dp / (v.magnitude() * u.magnitude()))

class Vector2:
    def __init__(self, x_or_list=0, y=0, theta=None) -> None:
        if theta is not None:
            self.x = cos(theta)
            self.y = sin(theta)
        elif not is_scalar(x_or_list):
            self.x = x_or_list[0]
            self.y = x_or_list[1]
        else:
            self.x = x_or_list
            self.y = y

    def copy(self):
        """
        return: a copy of the current vector.
        """
        return Vector2(self.x, self.y)

    def apply_func(self, func):
        """
        return: a copy of the vector with a specified function applied to each element.
        """
        v_copy = self.copy()
        for i, v in enumerate(v_copy):
            v_copy[i] = func(v)
        return v_copy

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        return list(self)[index]
    
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
            return
        if index == 1:
            self.y = value
        return
    
    def __len__(self):
        return 2
    
    def __neg__(self): # -Vector2
        return self.__mul__(-1)
    
    def __pos__(self): # +Vector2
        return self

    def __add__(self, other): # Vector2 + Vector2
        if is_vector2(other):
            return Vector2(self.x + other.x, self.y + other.y)
        return None
    
    def __iadd__(self, other): # self += other
        if is_vector2(other):
            self.x += other.x
            self.y += other.y
        return self

    def __sub__(self, other): # Vector2 - Vector2
        if is_vector2(other):
            return self.__add__(-other)
        return None
    
    def __isub__(self, other): # self -= other
        if is_vector2(other):
            self.x -= other.x
            self.y -= other.y
        return self
    
    def __mul__(self, other): # Vector2 * Vector2 | Vector2 * Scalar
        if is_scalar(other):
            return Vector2(self.x * other, self.y * other)
        else:
            return Vector2(self.x * other.x, self.y * other.y)

    def __rmul__(self, other): # Vector2 * Vector2 | Scalar * Vector2
        if is_scalar(other):
            return Vector2(self.x * other, self.y * other)
        else:
            return Vector2(self.x * other.x, self.y * other.y)
        
    def __imul__(self, other): # self *= other
        if is_scalar(other):
            self.x *= other
            self.y *= other
        else:
            self.x *= other.x
            self.y *= other.y
        return self
    
    def __truediv__(self, other): # Vector2 / Vector2 | Vector2 / Scalar
        if is_scalar(other):
            return Vector2(self.x / other, self.y / other)
        else:
            return Vector2(self.x / other.x, self.y / other.y)

    def __rtruediv__(self, other): # Vector2 / Vector2 | Scalar / Vector2
        if is_scalar(other):
            return Vector2(other / self.x, other / self.y)
        else:
            return Vector2(other.x / self.x, other.y / self.y)

    def __pow__(self, other): # Vector2 ^ Scalar
        if is_scalar(other):
            return Vector2(self.x ** other, self.y ** other)
        return None
    
    def __str__(self):
        return f"X: {self.x} Y: {self.y}"

    def clamp(self, _min, _max):
        if self.x > _max: self.x = _max
        if self.y > _max: self.y = _max

        if self.x < _min: self.x = _min
        if self.y < _min: self.y = _min
    
    def rotate(self, theta) -> 'Vector2': # Rotate
        """
        return: a copy of the vector rotated by the specified angle.
        """
        s, c = sin(theta), cos(theta)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)
    
    def dot(self, other) -> float: # Dot Product <Scalar>
        if is_vector2(other):
            return self.x * other.x + self.y * other.y
        return None
    
    def cross(self, other) -> 'Vector2': # Cross Product <Scalar>
        if is_vector2(other):
            return self.x * other.y - self.y * other.x
        return None
    
    def magnitude(self) -> float:
        return sqrt(self.x*self.x + self.y*self.y)
    
    def normalize(self) -> 'Vector2': # normalized of Vector2
        mag = self.magnitude()
        if mag == 0: return Vector2()
        return self / mag
    
    def distance(self, other) -> float:
        if is_vector2(other):
            return (self - other).magnitude()
        return None
    
    def get_angle(self) -> float: # angle with Vector2(1, 0)
        return atan2(self.y, self.x)

class Vector3:
    def __init__(self, x_or_list=0, y=0, z=0) -> None:
        if not is_scalar(x_or_list) and len(x_or_list) >= 3:
            self.x = x_or_list[0]
            self.y = x_or_list[1]
            self.z = x_or_list[2]
        else:
            self.x = x_or_list
            self.y = y
            self.z = z

    def copy(self) -> 'Vector3':
        """
        return: a copy of the current vector.
        """
        return Vector3(self.x, self.y, self.z)

    def apply_func(self, func):
        """
        return: a copy of the vector with a specified function applied to each element.
        """
        v_copy = self.copy()
        for i, v in enumerate(v_copy):
            v_copy[i] = func(v)
        return v_copy

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, index):
        return list(self)[index]
    
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
            return
        if index == 1:
            self.y = value
            return
        if index == 2:
            self.z = value
        return
    
    def __len__(self):
        return 3
    
    def __neg__(self): # -Vector3
        return self.__mul__(-1)
    
    def __pos__(self): # +Vector3
        return self

    def __add__(self, other): # Vector3 + Vector3
        if is_vector3(other):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        return None
    
    def __iadd__(self, other): # self += other
        if is_vector3(other):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        return self
    
    def __sub__(self, other): # Vector3 - Vector3
        if is_vector3(other):
            return self.__add__(-other)
        return None
    
    def __isub__(self, other): # self -= other
        if is_vector3(other):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        return self
    
    def __mul__(self, other): # Vector3 * Vector3 | Vector3 * Scalar
        if is_scalar(other):
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __rmul__(self, other): # Vector3 * Vector3 | Scalar * Vector3
        if is_scalar(other):
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other)
        
    def __imul__(self, other): # self *= other
        if is_scalar(other):
            self.x *= other
            self.y *= other
            self.z *= other
        elif is_vector3(other):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        return self

    def __truediv__(self, other): # Vector3 / Vector3 | Vector3 / Scalar
        if is_scalar(other):
            return Vector3(self.x / other, self.y / other, self.z / other)
        else:
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)

    def __rtruediv__(self, other): # Vector3 / Vector3 | Scalar / Vector3
        if is_scalar(other):
            return Vector3(other / self.x, other / self.y, other / self.z)
        else:
            return Vector3(other.x / self.x, other.y / self.y, other.z / self.z)

    def __pow__(self, other): # Vector3 ^ Scalar
        if is_scalar(other):
            return Vector3(self.x ** other, self.y ** other, self.z ** other)
        return None
    
    def __str__(self):
        return f"X: {self.x} Y: {self.y} Z: {self.z}"
    
    def clamp(self, _min, _max):
        if self.x > _max: self.x = _max
        if self.y > _max: self.y = _max
        if self.z > _max: self.z = _max

        if self.x < _min: self.x = _min
        if self.y < _min: self.y = _min
        if self.z < _min: self.z = _min
    
    def rotateX(self, theta) -> 'Vector3':
        """
        return: a copy of the vector rotated around the x-axis by the specified angle.
        """
        c, s = cos(theta), sin(theta)
        return Vector3(self.x, self.y * c + self.z * s, self.z * c - self.y * s)

    def rotateY(self, theta) -> 'Vector3':
        """
        return: a copy of the vector rotated around y-axis by the specified angle.
        """
        c, s = cos(theta), sin(theta)
        return Vector3(self.x * c + self.z * s, self.y, self.z * c - self.x * s)
    
    def rotateZ(self, theta) -> 'Vector3':
        """
        return: a copy of the vector rotated around z-axis by the specified angle.
        """
        c, s = cos(theta), sin(theta)
        return Vector3(self.x * c - self.y * s, self.x * s + self.y * c, self.z)
    
    def dot(self, other) -> float: # Dot Product <Scalar>
        if is_vector3(other):
            return self.x * other.x + self.y * other.y + self.z * other.z
        return None
    
    def cross(self, other) -> 'Vector3': # Cross Product <Vector3>
        if is_vector3(other):
            return Vector3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)
        return None
    
    def magnitude(self) -> float: # magnitude of Vector3
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    
    def normalize(self) -> 'Vector3': # normalized of Vector3
        mag = self.magnitude()
        if mag == 0: return Vector3()
        return self / mag
    
    def distance(self, other) -> float:
        if is_vector3(other):
            return (self - other).magnitude()
        return None