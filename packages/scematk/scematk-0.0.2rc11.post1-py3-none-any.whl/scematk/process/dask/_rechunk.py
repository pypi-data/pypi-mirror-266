from .._process import Process
from ...image._image import Image

class Rechunk(Process):
    def __init__(self, chunks: tuple):
        super().__init__(f'Rechunk image to {str(chunks)}')
        self.chunks = chunks

    def run(self, image: Image) -> Image:
        image.rechunk(self.chunks)
        return image