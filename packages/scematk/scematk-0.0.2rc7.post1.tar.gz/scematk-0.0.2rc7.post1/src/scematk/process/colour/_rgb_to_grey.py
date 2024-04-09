from .._process import Process
from ...image._image import Image
from ...image._ubyte_image import UByteImage
import dask.array as da
from skimage import img_as_ubyte
from skimage.color import rgb2gray

class RGBToGrey(Process):
    def __init__(self):
        super().__init__('Convert an RGB UByte Image to a Greyscale UByte Image')

    def run(self, image: Image) -> Image:
        assert isinstance(image, UByteImage)
        assert image.ndim == 3
        assert image.shape[2] == 3
        assert image.channel_names == ["Red", "Green", "Blue"]
        img = image.image
        grey_img = da.map_blocks(lambda x: img_as_ubyte(rgb2gray(x)), img, drop_axis=2, dtype='uint8')
        grey_img = da.expand_dims(grey_img, axis=2)
        return UByteImage(grey_img, image.info, ["Grey"])