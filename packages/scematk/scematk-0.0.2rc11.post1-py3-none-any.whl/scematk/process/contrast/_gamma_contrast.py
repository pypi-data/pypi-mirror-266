from .._process import Process
from ...image._image import Image
from ...image._ubyte_image import UByteImage

class GammaContrast(Process):
    def __init__(self, gamma: float = 1.0):
        super().__init__(f"Contrast adjustment using gamma correction of {str(gamma)}")
        assert isinstance(gamma, float) or isinstance(gamma, int), "gamma must be convertable to float."
        self.gamma = gamma

    def run(self, image: Image) -> Image:
        assert isinstance(image, Image), "image must be of type Image."
        if not isinstance(image, UByteImage):
            raise NotImplementedError("GammaContrast only supports UByteImage at this time. Please raise an issue to change this.")
        img = image.image
        gamma = self.gamma
        if isinstance(image, UByteImage):
            img = img/255.0
        img = img ** gamma
        if isinstance(image, UByteImage):
            img = img*255.0
            img = img.astype('uint8')
            return UByteImage(img, image.info, image.channel_names)
        else:
            raise NotImplementedError("GammaContrast only supports UByteImage at this time. Please raise an issue to change this.")

