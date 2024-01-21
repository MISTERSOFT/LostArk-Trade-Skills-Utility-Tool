from core import EasyOCROCRStrategy, OCR
import cv2

ocr = OCR(EasyOCROCRStrategy())

img = cv2.imread("text_detection_repair_tool_required.jpg")

ocr.extract_text_from_image(img)
