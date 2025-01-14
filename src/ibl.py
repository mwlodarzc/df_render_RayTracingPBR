import numpy as np
import taichi as ti
from taichi.math import vec2, vec3


from .camera import camera_gamma
from .dataclass import Ray
from .postprocessor import adjust
from .util import sample_spherical_map


@ti.data_oriented
class Image:
    def __init__(self, path: str):
        img = ti.tools.imread(path).astype(np.float32)
        self.img = vec3.field(shape=img.shape[:2])
        self.img.from_numpy(img / 255)

    @ti.kernel
    def process(self, exposure: float, gamma: float):
        for i, j in self.img:
            color = self.img[i, j]
            self.img[i, j] = adjust(color, exposure, gamma)

    @ti.func
    def texture(self, uv: vec2) -> vec3:
        x = int(uv.x * self.img.shape[0])
        y = int(uv.y * self.img.shape[1])
        return self.img[x, y]


hdr_map = Image('assets/Tokyo_BigSight_3k.hdr')
hdr_map.process(exposure=1.4, gamma=camera_gamma)


@ti.func
def sky_color(ray: Ray) -> vec3:
    uv = sample_spherical_map(ray.direction)
    color = hdr_map.texture(uv)
    return color
