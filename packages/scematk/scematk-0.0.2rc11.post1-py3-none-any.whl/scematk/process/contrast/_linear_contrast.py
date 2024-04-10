from .._process import Process
from ...image._image import Image
from ...image._ubyte_image import UByteImage
import dask.array as da

class LinearContrast(Process):
    def __init__(self, slope: float = 1.0, intercept: float = 0.0):
        super().__init__(f"Contrast adjustment using linear correctionwith a slope of {str(slope)} and an intercept of {str(intercept)}")
        assert isinstance(slope, float) or isinstance(slope, int), "slope must be convertable to float."
        assert isinstance(intercept, float) or isinstance(intercept, int), "intercept must be convertable to float."
        self.slope = slope
        self.intercept = intercept

    def run(self, image: Image) -> Image:
        assert isinstance(image, Image), "image must be of type Image."
        if not isinstance(image, UByteImage):
            raise NotImplementedError("GammaContrast only supports UByteImage at this time. Please raise an issue to change this.")
        img = image.image
        slope = self.slope
        intercept = self.intercept
        if isinstance(image, UByteImage):
            img = img/255.0
        img = img * slope + intercept
        img = da.clip(img, 0, 1)
        if isinstance(image, UByteImage):
            img = img*255.0
            img = img.astype('uint8')
            return UByteImage(img, image.info, image.channel_names)
        else:
            raise NotImplementedError("GammaContrast only supports UByteImage at this time. Please raise an issue to change this.")