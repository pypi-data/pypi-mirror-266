import numpy as np
from matplotlib.transforms import Affine2D
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def show_paths_with_patch_prop(ax, paths, update_lim=True,
               show_i=False, start_i=0):
    ee = []
    for i, (p, patch_prop) in enumerate(paths, start_i):
        patch = PathPatch(p, label=f"{i}")
        kv = dict((k, v) for k, v in patch_prop.items() if hasattr(patch, f"set_{k}"))
        patch.set(**kv)
        if show_i:
            patch.set_fc(f"C{i}")
        ax.add_patch(patch)
        ee.append(p.get_extents())

    if show_i:
        ax.legend(bbox_to_anchor=(1, 1), loc=2)

    if update_lim:
        e0 = ee[0].union(ee)
        ax.set(xlim=(e0.xmin, e0.xmax), ylim=(e0.ymin, e0.ymax))

def show_paths_with_gc_prop(ax, paths, update_lim=True,
                            show_i=False, start_i=0):
    paths = [(p, dict(fc=rgbFace, ec=gc_prop["foreground"],
                      linewidth=gc_prop.get("linewidth", 1))) for p, gc_prop, rgbFace in paths]
    show_paths_with_patch_prop(ax, paths, update_lim=update_lim,
                               show_i=show_i, start_i=start_i)


class PathsStretcher:
    """Given the list of paths, stretch them by translating control points
    higher then a threshold. It was meant to be used to draw fancy bars. Its
    instance is a callable object who takes a height of the bar, facecolor and
    edgecolor, returns an iterator of (path, a dict of gc properties,
    facecolor) which will be fed into the renderer's draw_path method.
    """

    def __init__(self, paths, height, y_thresh,
                 height_lim=-np.inf,
                 low_height_mode="tranlate",
                 paths_toggle=None,
                 height_toggle=None,
                 fn_get_color=None,
                 ):
        """

        low_height_mode : behavior when height is less then the limit. "translate" to translate the path down. Other values to keep the path at the limit height.
        dy_lim : if dy is lower than dy, do not try to make it smaller byt translate the path as a whole down.
        paths_toggle, dy_toggle: paths_toggle is drawn only if dy is larger then dy_toggle.

        fn_get_color : should have a signature of get_color(i, p, fc, ec, fc_new, ec_new). (i, p, fc, ec) is from the svg object, fc_new, ec_new is from the draw method. Should return (fc, ec).

        """
        self._paths = paths
        self._height = height
        self._y_thresh = y_thresh
        self._paths_toggle = paths_toggle
        self._height_toggle = height_toggle
        self._height_lim = height_lim
        self._low_height_mode = low_height_mode
        self._fn_get_color = fn_get_color

    def _get_color(self, i, p, fc, ec, fc_new, ec_new):
        if self._fn_get_color is not None:
            fc, ec = self._fn_get_color(i, p, fc, ec, fc_new, ec_new)

        return fc, ec

    def __call__(self, height, fc_new, ec_new="k"):
        dy = height - self._height

        tr = Affine2D()
        if height < self._height_lim:
            # print("dy too low")
            if self._low_height_mode == "translate":
                tr.translate(0, height - self._height_lim)
            dy = self._height_lim - self._height

        for i, (p, d) in enumerate(self._paths):
            fc, ec = d["fc"], d["ec"]
            fc, ec = self._get_color(i, p, fc, ec, fc_new, ec_new)

            v = p.vertices.copy()
            y = v[:, 1]

            y[y > self._y_thresh] += dy
            yield tr.transform_path(Path(v, codes=p.codes)), dict(foreground=ec, alpha=1), fc

        if ( (self._paths_toggle is not None) and (self._height_toggle is not None)
             and height >= self._height_toggle):

            for i, (p, d) in enumerate(self._paths_toggle):
                fc, ec = d["fc"], d["ec"]
                yield tr.transform_path(p), dict(foreground=ec, alpha=1), fc


def get_normalizing_transform(bbox):
    "return a affine transform that make the input bbox has a bottom at 0 and its width spans from -0.5 to 0.5"
    x0 = 0.5 * (bbox.xmin + bbox.xmax)
    w = bbox.width
    h = bbox.height #e0.ymax - e0.ymin)

    tr = Affine2D().translate(-x0, -bbox.ymin).scale(1./w)

    return tr, h/w

