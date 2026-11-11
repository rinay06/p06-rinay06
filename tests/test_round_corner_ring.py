# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from thumbor.ext.filters import _round_corner

WIDTH = 200
HEIGHT = 150
RADIUS = 60


def test_transparent_round_corner_has_no_dark_ring():
    # Solid opaque white picture. With a transparent corner, every pixel
    # that is still visible (alpha > 0) must stay white: the antialiased
    # edge may only fade alpha, never darken the colour.
    data = bytes([255, 255, 255, 255]) * (WIDTH * HEIGHT)

    result = _round_corner.apply(
        1, "RGBA", RADIUS, RADIUS, 255, 255, 255, WIDTH, HEIGHT, data, 1
    )

    dark_ring = []
    partial_alpha = 0
    for index in range(0, len(result), 4):
        red, green, blue, alpha = result[index : index + 4]
        if alpha > 0 and (red, green, blue) != (255, 255, 255):
            dark_ring.append((index // 4, (red, green, blue, alpha)))
        if 0 < alpha < 255:
            partial_alpha += 1

    assert not dark_ring, (
        f"{len(dark_ring)} visible pixels were darkened, e.g. {dark_ring[:3]}"
    )
    # the curve must be antialiased through alpha
    assert partial_alpha > 0
