import pytesseract
from abc import ABC, abstractmethod


class OCRStrategy(ABC):
    @abstractmethod
    def image_to_text(self, img) -> list[str]:
        pass


class PytesseractOCRStrategy(OCRStrategy):
    """
    Strategy to use Pytesseract OCR
    """

    def image_to_text(self, img) -> list[str]:
        result = pytesseract.image_to_string(img)
        return [result]


class EasyOCROCRStrategy(OCRStrategy):
    """
    Strategy to use EasyOCR
    """

    def image_to_text(self, img) -> list[str]:
        """
        TODO
        """
        raise NotImplementedError()
        # return super().image_to_text(img)


class OCR:
    def __init__(self, strategy: OCRStrategy) -> None:
        self._strategy = strategy

    def extract_text_from_image(self, img) -> list[str]:
        """
        Extract text from image.
        """
        return self._strategy.image_to_text(img)
