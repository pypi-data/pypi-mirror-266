"""
Gives the name of any RGB color.

If the exact color doesn't have a name, the closest match will be used instead.
"""

__all__ = ["find"]

import functools

from cores.const.common.color_const import ColorNames


@functools.singledispatch
def find(r=0, g=0, b=0):
    """Finds a color's name.

    The color may be expressed in either of the following formats:
     - three ints (r, g, b) in the range 0 <= x < 256,
     - a tuple of three ints (r, g, b) in the range 0 <= x < 256, or
     - a hexadecimal representation (3 or 6 digits, '#' prefix optional).
    """
    if type(r) is not int or type(g) is not int or type(b) is not int:
        raise TypeError("R, G and B values must be int")
    if not (0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256):
        raise ValueError("Invalid color value: must be 0 <= x < 256")
    return _search(ColorNames.search_tree, r, g, b)


@find.register(str)
def find_hex(color):
    if color[0] == '#':
        color = color[1:]
    if len(color) == 3:
        return find(*[int(c * 2, 16) for c in color])
    if len(color) == 6:
        return find(*[int(color[i:i + 2], 16) for i in (0, 2, 4)])
    raise ValueError("Malformed hexadecimal color representation")


@find.register(tuple)
def find_tuple(color):
    if len(color) != 3:
        raise ValueError("Malformed color tuple: must be of size 3 (r, g, b)")
    return find(*color)


def _octree_index(r, g, b, d):
    return ((r >> d & 1) << 2) | ((g >> d & 1) << 1) | (b >> d & 1)


def _search(tree, r, g, b, d=7):
    i = _octree_index(r, g, b, d)
    if i not in tree:
        return _approximate(tree, r, g, b)
    return tree[i] if type(tree[i]) is str else _search(tree[i], r, g, b, d - 1)


def _approximate(tree, r, g, b):
    def _distance(colorname):
        x, y, z = ColorNames.colors[colorname]
        return (r - x) ** 2 + (g - y) ** 2 + (b - z) ** 2

    return min(_descendants(tree), key=_distance)


def _descendants(tree):
    for i, child in tree.items():
        if type(child) is str:
            yield child
        else:
            yield from _descendants(child)
