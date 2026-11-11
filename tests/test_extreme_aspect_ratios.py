# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES = abspath(join(dirname(__file__), "../course/images"))


class ExtremeAspectRatioTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    async def fetch_image(self, path):
        response = await self.async_fetch(path)
        assert response.code == 200
        return Image.open(BytesIO(response.body))

    @gen_test
    async def test_very_wide_crop_of_transparent_image_is_not_empty(self):
        image = await self.fetch_image("/unsafe/800x20/rainbow.png")

        assert image.size == (800, 20)
        rgba = image.convert("RGBA")
        _, alpha_max = rgba.getchannel("A").getextrema()
        assert alpha_max > 0, "every pixel is fully transparent"
        # the coloured bars of the source must show up in the strip
        colors = rgba.getcolors(maxcolors=800 * 20)
        assert len(colors) > 2

    @gen_test
    async def test_fit_in_very_wide_source_into_one_pixel_box(self):
        image = await self.fetch_image("/unsafe/fit-in/1x1/940x2.png")

        assert image.size == (1, 1)

    @gen_test
    async def test_fit_in_with_width_only(self):
        image = await self.fetch_image("/unsafe/fit-in/100x0/940x2.png")

        assert image.size == (100, 1)
