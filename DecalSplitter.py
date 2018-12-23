import os
import sys
from pathlib import Path

from PIL import Image

if len(sys.argv) > 1:
    texture = Path(sys.argv[1])
else:
    texture = Path(
        r"E:\PYTHON_STUFF\OVL_IO\JWEDinos\Shared\DinosaurCommon\DinosaurCommon\anky_ankylo_backplates.pbasecolourtexture.tga")

im = Image.open(texture.open('rb'))  # type: Image.Image
tex_size = im.size[0]
for i in range(im.size[1] // tex_size):
    offset = i * tex_size
    print(offset, offset + tex_size)
    layer = Image.new('RGB', (tex_size, tex_size))
    layer.paste(im.crop((0, offset, tex_size, offset + tex_size)))
    temp = Path(texture)

    temp = temp.with_name(texture.stem + '_{}.png'.format(i))
    temp = temp.parent / texture.stem / temp.name
    os.makedirs(temp.parent, exist_ok=True)
    layer.save(temp)
