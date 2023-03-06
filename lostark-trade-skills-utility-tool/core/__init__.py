from .singleton import MetaSingleton
from .log_service import LogService
from .ocr import OCR, EasyOCROCRStrategy, PytesseractOCRStrategy
from .windowcapture import WindowCapture

logger = LogService()
