from .utils import resource_path
import pytesseract
import easyocr
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
        reader = easyocr.Reader(
            lang_list=["fr"],
            gpu=False,
            model_storage_directory=resource_path("assets/ocr_models"),
            download_enabled=False,
        )
        raw_result = reader.readtext(img)  # "text_detection_repair_tool_required.jpg"
        result = [text for (coords, text, recognition_accuracy) in raw_result]
        print(result)
        # raise NotImplementedError()
        # return super().image_to_text(img)
        return result


class OCR:
    def __init__(self, strategy: OCRStrategy) -> None:
        self._strategy = strategy

    def extract_text_from_image(self, img) -> list[str]:
        """
        Extract text from image.
        """
        return self._strategy.image_to_text(img)
