# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

STICKER = abspath(join(dirname(__file__), "../course/images/sticker.gif"))


def count_transparent(image):
    alpha = image.convert("RGBA").getchannel("A")
    return alpha.tobytes().count(0)


def alpha_values(image):
    return set(image.convert("RGBA").getchannel("A").tobytes())


def make_engine():
    config = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    return Engine(Context(config=config))


def test_resized_palette_gif_keeps_its_transparent_background():
    with open(STICKER, "rb") as sticker_file:
        source_bytes = sticker_file.read()

    source = Image.open(BytesIO(source_bytes))
    assert "transparency" in source.info
    assert count_transparent(source) > 0

    engine = make_engine()
    engine.load(source_bytes, ".gif")
    engine.resize(240, 160)

    result = Image.open(BytesIO(engine.read(".gif")))

    # the resized GIF must carry a transparency index ...
    assert result.info.get("transparency") is not None
    # ... and the background must still be transparent, not a black box
    assert count_transparent(result) > 0


def test_resized_opaque_palette_gif_stays_opaque():
    source = Image.effect_mandelbrot((60, 60), (-3, -2.5, 2, 2.5), 20)
    buffer = BytesIO()
    source.convert("P").save(buffer, "GIF")

    engine = make_engine()
    engine.load(buffer.getvalue(), ".gif")
    engine.resize(120, 120)

    result = Image.open(BytesIO(engine.read(".gif")))

    assert result.info.get("transparency") is None
    assert alpha_values(result) == {255}


def test_resized_palette_png_keeps_partial_alpha():
    source = Image.new("RGBA", (40, 40), (255, 0, 0, 255))
    for x_pos in range(40):
        for y_pos in range(20):
            source.putpixel(
                (x_pos, y_pos),
                (0, 0, 255, 128) if x_pos < 20 else (0, 0, 0, 0),
            )
    buffer = BytesIO()
    source.save(buffer, "PNG")

    engine = make_engine()
    engine.load(buffer.getvalue(), ".png")
    engine.original_mode = "P"
    engine.resize(80, 80)

    result = Image.open(BytesIO(engine.read(".png")))

    assert 128 in alpha_values(result)
