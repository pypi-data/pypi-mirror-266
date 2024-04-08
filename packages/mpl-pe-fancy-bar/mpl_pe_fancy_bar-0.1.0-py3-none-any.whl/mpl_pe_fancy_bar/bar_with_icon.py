from matplotlib.path import Path
from matplotlib.transforms import Affine2D
from mpl_pe_fancy_bar import BarTransformBase

from collections import namedtuple
ViewPort = namedtuple("ViewPort", ["x", "y", "w", "h"])


class Icon:
    def __init__(self, viewport: tuple[int], path: Path, flip=True):
        if len(viewport) == 2:
            self._viewport = ViewPort(0, 0, *viewport)
        elif len(viewport) == 4:
            self._viewport = ViewPort(*viewport)
        else:
            raise ValueError()

        self._vertices = [0, 1] + (path.vertices - self._viewport[:2]) / [self._viewport[2], -self._viewport[3]]
        self._codes = path.codes

    def get(self, ax, ay, scale, scaley=None, tx=0, ty=0, rotate_deg=0):
        """

        rotate_deg : deg in CCW
        """
        if scaley is None:
            scaley = scale
        vertices = (Affine2D()
                    .translate(-ax, -ay)
                    .rotate_deg(rotate_deg)
                    .scale(scale, scaley)
                    .translate(tx, ty)
                    .transform(self._vertices))

        return Path(vertices=vertices, codes=self._codes)


class BarWithIcon(BarTransformBase):
    def __init__(self, icon, scale=0.6, dh=0.5, orientation="vertical",
                 rotate_deg=None):
        super().__init__(orientation)
        self._icon = icon
        self._scale = scale
        self._dh = dh
        self._rotate_deg = rotate_deg

    def _get_surface(self, h):
        rotate_deg = self._rotate_deg
        if rotate_deg is None:
            if self.get_orientation() == "vertical":
                rotate_deg = 0
            else:
                rotate_deg = -90

        path = self._icon.get(0.5, 0.5, scale=self._scale,
                              rotate_deg=-90,
                              tx=0, ty=h-self._dh)
        # v0 = Affine2D().rotate_deg(90).transform(icon.vertices / 512. - 0.5)
        # vertices = v0 * self._scale + [0, h-self._dh]
        # circle = Path(vertices=vertices, codes=icon.codes)
        return path


if False:
    ii = Icon((512, 512), icon)
    from matplotlib.patches import PathPatch
    fig2, ax2 = plt.subplots(num=2, clear=True)
    ax2.set_aspect(1)
    # ax2.add_patch(PathPatch(icon, ec="k", fc="gold"))
    # ax2.set(xlim=(-10, 522), ylim=(512, 0))

    ii = Icon((512, 512), icon)
    pp = ii.get(0., 0, 100, rotate_deg=10)

    # ax2.cla()
    ax2.plot(*pp.vertices.T)
