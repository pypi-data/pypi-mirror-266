import numpy as np
from matplotlib.path import Path
import matplotlib.transforms as mtransforms
from matplotlib.transforms import Bbox
from matplotlib.transforms import Affine2D, IdentityTransform
import matplotlib.colors as mcolors
from mpl_visual_context.patheffects_base import ChainablePathEffect, AbstractPathEffect
from mpl_visual_context.bezier_helper import get_inverted_path


class BarOrientationHelper:
    def __init__(self, orientation="vertical"):
        assert orientation in ["vertical", "horizontal"]
        self._orientation = orientation

    def _get_surface_transform(self, width, height):
        # return IdentityTransform()
        if self._orientation == "vertical":
            return Affine2D().scale(1, width/height)
        else:
            return Affine2D().scale(height/width, 1)

    def get_orientation(self):
        return self._orientation

    @staticmethod
    def get_width_height(tpath, affine):

        tpp = affine.transform_path(tpath)
        # we get the height and the width of the bar
        height_vector = 0.5*((tpp.vertices[2]+tpp.vertices[3])
                              - (tpp.vertices[0]+tpp.vertices[1]))
        height = (height_vector**2).sum()**.5
        width = (((tpp.vertices[0]+tpp.vertices[3])
                   - (tpp.vertices[1]+tpp.vertices[2]))**2).sum()**.5*0.5

        return height_vector, width, height

    @staticmethod
    def get_height_in_data(screen_to_data, tpath, affine):
        """
        Return the height of the bar in "data" coordinate.
        """
        # This was originally used in the mpl-poormans-3d. Not sure if this is still useful.

        tpp = affine.transform_path(tpath)
        tpp = screen_to_data.transform_path(tpp)
        # we get the height and the width of the bar
        height_vector = -0.5*((tpp.vertices[2]+tpp.vertices[3])
                              - (tpp.vertices[0]+tpp.vertices[1]))
        height = (height_vector**2).sum()**.5

        return height

    def get_height_and_affine(self, tpath, affine):
        if tpath != Path.unit_rectangle():
            raise RuntimeError("path much be a unit_rect")

        # The unit_rectangle has (0, 0) at botton left and (1, 1) at top right.
        # We change the path and affine so that the surface has a center at 0,
        # 0 and that corresponds to the bottom center of the bar.
        if self._orientation == "vertical":
            tpath  = Affine2D().translate(-0.5, 0).transform_path(tpath)
            affine = Affine2D().translate(0.5, 0) + affine
        else:
            tpath  = Affine2D().translate(0., -0.5).transform_path(tpath)
            affine = Affine2D().translate(0., 0.5) + affine

        height_vector, width, height = self.get_width_height(tpath, affine)

        orientation = self.get_orientation()
        surface_affine = self._get_surface_transform(width, height)
        new_affine = surface_affine + affine

        if orientation == "vertical":
            h = height/width
        else:
            h = width/height
            new_affine = new_affine + Affine2D().rotate_deg(-90)

        return h, new_affine


class BarTransformBase(ChainablePathEffect, BarOrientationHelper):
    def __init__(self, orientation="vertical"):
        BarOrientationHelper.__init__(self, orientation)
        ChainablePathEffect.__init__(self)

    def _get(self, tpath, affine):
        height_vector, width, height = self.get_width_height(tpath, affine)
        if self.get_orientation() == "vertical":
            surface = self._get_surface(height/width)
        else:
            surface = self._get_surface(width/height)
            surface = Affine2D().rotate_deg(-90).transform_path(surface)

        # _get_surface_transform takes care of the orientation.
        surface_affine = self._get_surface_transform(width, height)

        return surface, surface_affine + affine, height_vector

    def _get_surface(self, h):
        """
        h : height of the bar. Width is assumed to be 1
        """
        surface = Path(vertices=[[-0.5, 0],
                                 [0.5, 0],
                                 [0.5, h],
                                 [-0.5, h]],
                       closed=True)

        return surface

    def _convert(self, renderer, gc, tpath, affine, rgbFace):

        if tpath != Path.unit_rectangle():
            raise RuntimeError("path much be a unit_rect")

        # The unit_rectangle has (0, 0) at botton left and (1, 1) at top right.
        # We change the path and affine so that the surface has a center at 0,
        # 0 and that corresponds to the bottom center of the bar.
        if self._orientation == "vertical":
            tpath  = Affine2D().translate(-0.5, 0).transform_path(tpath)
            affine = Affine2D().translate(0.5, 0) + affine
        else:
            tpath  = Affine2D().translate(0., -0.5).transform_path(tpath)
            affine = Affine2D().translate(0., 0.5) + affine

        surface, affine, height_vector = self._get(tpath, affine)
        # set clip on the col using gc information

        return renderer, gc, surface, affine, rgbFace


class BarToArrow(BarTransformBase):
    def __init__(self, width=0.15, width2=None):
        """
        width: width of the arrow
        width2: width of the vertical part
        """

        super().__init__()
        self._width = width
        self._width2 = width2

    def _get_surface(self, height):
        """
        height of the bar normalized by the bar width.
        """

        # For now, the surface should have coordinates of [-0.5, 0] at LLC, and [0.5, h] at TRC.

        h = height
        # h = 10
        w = self._width
        w2 = self._width if self._width2 is None else self._width2

        sqrt2 = 1.4142135623730951
        M, C3, L = Path.MOVETO, Path.CURVE3, Path.LINETO
        path_right = [
            ([0, h], M), # we start from the tip of the arrow
            ([w*(sqrt2-1), h], C3),
            ([w*(sqrt2-0.5), (h-0.5*w)], C3),

            ([0.5-0.5*w*sqrt2, h-0.5+1.5*w*sqrt2-w], L),
            ([0.5, h-0.5+w*sqrt2-w], C3),
            ([0.5-0.5*w*sqrt2, h-0.5+0.5*w*sqrt2-w], C3),

            ([0.5-w*sqrt2, h-0.5-w], C3),
            ([0.5-1.5*w*sqrt2, h-0.5+0.5*w*sqrt2-w], C3),

            ([w2, h-w*sqrt2-w2-w], L), # start of the vertical part
            ([w2, w2], L),
            ([w2, 0], C3),
            ([0, 0], C3),
        ]
        vertices_right = np.array([v for v, _ in path_right])
        codes_right = [c for _, c in path_right]

        path_right = Path(vertices=vertices_right, codes=codes_right)

        path_left = get_inverted_path(path_right, close_poly=False)
        # slice of [1:] to remove the Path.MOVETO in the path_left.
        surface = Path(vertices=np.vstack([path_right.vertices,
                                           path_left.vertices[1:]*[-1, 1],
                                           path_right.vertices[0]]),
                       codes=np.concatenate([path_right.codes,
                                             path_left.codes[1:],
                                             [Path.CLOSEPOLY]]))

        return surface


class BarToRoundBar(BarTransformBase):
    def __init__(self, dh=0.5, orientation="vertical"):
        super().__init__(orientation)
        self._dh = dh

    def _get_surface(self, height):
        # For now, the surface should have coordinates of [-0.5, 0] at LLC, and [0.5, h] at TRC.

        h = height

        M, L = Path.MOVETO, Path.LINETO
        vertices_right = [[0, 0], [0.5, 0], [0.5, h-self._dh]]
        codes_right = [M, L, L]

        vertices_left = [[-0.5, 0], [0, 0], [0, 0]]
        codes_left = [L, L, Path.CLOSEPOLY]

        arc = Path.arc(0, 180)
        vertices_arc = 0.5 * arc.vertices[1:] + [0., h-self._dh]
        vertices = np.vstack([vertices_right, vertices_arc, vertices_left])
        codes = np.concatenate([codes_right, arc.codes[1:], codes_left])
        surface = Path(vertices, codes=codes)

        return surface


# class BarTransformFromFuncPathOnly(ChainablePathEffect, BarOrientationHelper):
class BarToPath(ChainablePathEffect, BarOrientationHelper):
    def __init__(self, get_path, orientation="vertical"):
        BarOrientationHelper.__init__(self, orientation)
        AbstractPathEffect.__init__(self)
        self._get_path = get_path

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        h, new_affine = self.get_height_and_affine(tpath, affine)

        path_combined = self._get_path(h)
        return super()._convert(renderer, gc, path_combined, new_affine, rgbFace)


# class BarTransformFromFunc(AbstractPathEffect, BarOrientationHelper):
class BarToMultiplePaths(AbstractPathEffect, BarOrientationHelper):
    """Privded a callable object, it transform the bar to multiple paths. The
    callable should take arguments of height of the bar, facecolor and the
    edgecolor. The width is assumed to be 1. It should return an iterable of
    (path, dictionary of gc propererties, rgbFace), which will be fed into the
    draw_path method of the renderer.
    """
    def __init__(self, draw_func, orientation="vertical"):
        BarOrientationHelper.__init__(self, orientation)
        AbstractPathEffect.__init__(self)
        self._draw_func = draw_func

    # def get_combined_path(self, tpath, affine):
    #     h, new_affine = self.get_height_and_affine(tpath, affine)

    #     vertices = []
    #     codes = []
    #     for p, gc_prop, rgbFace in self._draw_func(h, None, None):
    #         vertices.append(p.vertices)
    #         codes.append(p.codes)

    #     return Path(vertices=np.vstack(vertices), codes=np.concatenate(codes)), new_affine

    def get_combined_path(self, h):
        vertices = []
        codes = []
        for p, gc_prop, rgbFace in self._draw_func(h, None, None):
            vertices.append(p.vertices)
            codes.append(p.codes)

        return Path(vertices=np.vstack(vertices), codes=np.concatenate(codes))

    def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
        h, new_affine = self.get_height_and_affine(tpath, affine)

        ec = gc.get_rgb()[:3]
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        for p, gc_prop, rgbFace in self._draw_func(h, rgbFace, ec):
            for k, v in gc_prop.items():
                getattr(gc0, f"set_{k}")(v)
            renderer.draw_path(gc0, p, new_affine,
                               rgbFace=mcolors.to_rgba(rgbFace) if rgbFace is not None else None)

    def path_only(self):
        return BarToPath(self.get_combined_path)
