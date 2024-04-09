from ..image._image import Image
from abc import ABC, abstractmethod

class Process(ABC):
    def __init__(self, name: str):
        assert isinstance(name, str), 'name must be a string'

    @abstractmethod
    def run(self, image: Image) -> Image:
        pass

class Processor():
    def __init__(self):
        self.processes = []

    def add_process(self, process: Process):
        assert isinstance(process, Process), 'process must be a Process'
        self.processes.append(process)

    def run(self, image: Image) -> Image:
        assert isinstance(image, Image), 'image must be an Image'
        image = image
        for process in self.processes:
            image = process.run(image)
        return image
