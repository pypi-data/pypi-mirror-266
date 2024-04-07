import os
from PIL import Image
from .image_data_reader import ImageDataReader

class ImageMetadataExtractor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.reader = None

    def extract_metadata(self):
        if not os.path.isfile(self.image_path):
           raise FileNotFoundError(f"Image file not found: {self.image_path}")

        self.reader = ImageDataReader(self.image_path)

    @property
    def raw(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.raw

    @property
    def prompt(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.positive

    @property
    def negative(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.negative

    @property
    def model(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.parameter.get("model")

    @property
    def cfg(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.parameter.get("cfg")

    @property
    def steps(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.parameter.get("steps")

    @property
    def sampler(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.parameter.get("sampler")

    @property
    def seed(self):
        if self.reader is None:
            raise ValueError("Metadata not extracted. Call extract_metadata() first.")

        return self.reader.parameter.get("seed")
    
    @property
    def tool(self):
        return self.reader.tool if self.reader else ""

    @property
    def seed(self):
        return self.reader.seed if self.reader else ""

    @property
    def width(self):
        return self.reader.width if self.reader else 0

    @property
    def height(self):
        return self.reader.height if self.reader else 0

    @property
    def workflow(self):
        return self.reader.workflow if self.reader else ""

    @property
    def parameters(self):
        return self.reader.parameters if self.reader else {}
