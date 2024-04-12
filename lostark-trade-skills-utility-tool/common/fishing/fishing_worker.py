from PySide6.QtCore import QRunnable, Slot, Signal, QObject
from .viewmodel import FishingViewModel
from core import (
    cv2utils,
    OCR,
    EasyOCROCRStrategy,
    WindowCapture,
    LogService,
)
from core.utils import clean_string
from core.enums import FishingStrategy, FishingFocusZone
import time
import datetime
import mouse
import cv2
import keyboard
import numpy as np

CAST_FISH_BAIT_COOLDOWN = 15  # 15min
WORK_ENERGY_REQUIRED_FOR_FISHING = 60

# Focus zone HSV colors (orange has better rewards)
ORANGE_ZONE_HSV_LOWER = [106, 238, 176]
ORANGE_ZONE_HSV_UPPER = [135, 255, 255]
YELLOW_ZONE_HSV_LOWER = [21, 163, 189]
YELLOW_ZONE_HSV_UPPER = [179, 255, 255]


class FishingWorkerSignals(QObject):
    """
    Defines the signals available from a running fishing worker thread.
    """

    running_changed = Signal(bool)
    """
    Runnning state changed
    """

    stopped = Signal()
    """
    Thread stopped
    """

    log = Signal(str, LogService.LogType)
    """
    Log text emitted
    """


class FishingWorker(QRunnable):
    def __init__(self, opts: FishingViewModel):
        super(FishingWorker, self).__init__()
        self.signals = FishingWorkerSignals()
        self.wc = WindowCapture()
        self.options = opts
        self.ocr = OCR(EasyOCROCRStrategy())
        self.running = False

        self.hook_mark_img = cv2.imread(
            "assets/images/hook_mark.png", cv2.IMREAD_GRAYSCALE
        )
        self.repair_tools_icon_img = cv2.imread("assets/images/repair_tools_icon.jpg")
        self.vital_energy_icon_img = cv2.imread("assets/images/vital_energy_icon.jpg")
        self.fishing_mini_game_ready_icon_img = cv2.imread(
            "assets/images/fishing_mini_game_ready_icon.jpg"
        )

        self.fish_bait_casted_at = None
        self.can_cast_fishing = True
        self.is_fishing = False
        self.last_mouse_position = None
        self.usage_count_before_repair = 0
        # TODO: make a method to auto set `current_equiped_fishing_rod` depending on the currently equiped rod
        self.current_equiped_fishing_rod = self.options.fishing_strategy_rod_to_fish
        self.current_work_energy = 10500

    @Slot()
    def run(self):
        self.set_running(True)

        self.signals.log.emit(
            "Fishing will be started in 5 seconds !", LogService.LogType.INFO
        )
        time.sleep(5)
        self.signals.log.emit("Fishing started !", LogService.LogType.INFO)

        self.wc.focus_window()
        self.last_mouse_position = mouse.get_position()
        self.signals.log.emit(
            f"Default mouse position taken: {self.last_mouse_position}",
            LogService.LogType.INFO,
        )
        while self.running:
            if self.is_fishing is False:
                try:
                    can_fishing = self.has_work_energy()  # has_vital_energy()
                    if can_fishing is False:
                        self.signals.log.emit(
                            "Not enough work energy", LogService.LogType.ERROR
                        )
                        self.running = False
                except Exception as ex:
                    self.signals.log.emit(
                        f"Vital energy parsing failed but keep app running. Error: {str(ex)}",
                        LogService.LogType.WARNING,
                    )

            is_net_ready = self.is_fishing_net_ready()
            if is_net_ready:
                # switch to upgraded rod for easy mini game
                self.switch_fishing_rod()
                self.repair_fishing_rod()
                self.is_fishing = True
                x, y = self.last_mouse_position
                mouse.move(x, y)
                time.sleep(1)
                self.play_mini_game()
                # switch back rod
                self.switch_fishing_rod()
                x, y = self.last_mouse_position
                mouse.move(x, y)
                time.sleep(1.5)
                self.is_fishing = False
                self.update_work_energy()
            else:
                if self.can_cast_fishing:
                    self.check_and_repair_fishing_rod()
                    self.cast_throw_fish_bait()
                    self.update_work_energy()

                    self.signals.log.emit(
                        "Casting out lure", LogService.LogType.DEFAULT
                    )
                    keyboard.press_and_release(self.options.cast_lure_key)
                    self.can_cast_fishing = False
                    self.is_fishing = True
                    continue

                hooked = self.is_fish_hooked()
                if hooked:
                    self.usage_count_before_repair += 1
                    self.signals.log.emit(
                        "Detected catch! Reeling in lure", LogService.LogType.DEFAULT
                    )
                    keyboard.press_and_release(self.options.cast_lure_key)
                    self.can_cast_fishing = True
                    self.is_fishing = False
                    time.sleep(6)

        time.sleep(0.005)

        self.signals.log.emit("Fishing stopped !", LogService.LogType.INFO)
        self.signals.stopped.emit()

    def stop(self):
        self.set_running(False)

    def set_running(self, value: bool):
        self.running = value
        self.signals.running_changed.emit(self.running)

    def is_fishing_rod_need_repair(self):
        """
        Take screenshot of in-game chat area to check if the fishing rod needs to be repaired
        TODO: improve
        """

        chat_area_img = self.take_screenshot(0, 780, 700, 1080)

        img2gray = cv2.cvtColor(chat_area_img, cv2.COLOR_BGR2GRAY)
        ret, saturated_img = cv2.threshold(img2gray, 0, 255, cv2.THRESH_OTSU)

        # to manipulate the orientation of dilution, large x means horizonatally dilating  more,
        # large y means vertically dilating more
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 1))
        # dilate, more the iteration more the dilation
        dilated = cv2.dilate(saturated_img, kernel, iterations=9)

        # findContours returns 3 variables for getting contours
        contours, hierarchy = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Don't plot small false positives that aren't text (remove noisy empty area)
            if w < 35 and h < 35:
                continue

            text_block_cropped = chat_area_img[y : y + h, x : x + w]

            recognized_text = self.ocr.extract_text_from_image(text_block_cropped)[0]

            if "Réparez" in recognized_text or "Reparez" in recognized_text:
                self.signals.log.emit(
                    "Rod need to be repaired", LogService.LogType.WARNING
                )
                return True

        return False

    def extract_text_from_screenshot(
        self,
        screenshot: cv2.Mat,
        search: str,
        structuring_element_ksize: tuple[int, int] = (4, 3),
        dilate_iterations: int = 9,
    ):
        """
        Extract text locations from a given image.
        """

        hsv_lower = np.array([0, 0, 100])
        hsv_upper = np.array([255, 255, 255])
        mask = cv2.inRange(screenshot, hsv_lower, hsv_upper)

        results = {}  # texts locations

        # to manipulate the orientation of dilution, large x means horizonatally dilating  more,
        # large y means vertically dilating more
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, structuring_element_ksize)
        # dilate, more the iteration more the dilation
        dilated = cv2.dilate(mask, kernel, iterations=dilate_iterations)

        # findContours returns 3 variables for getting contours
        contours, hierarchy = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        recognized_texts = []

        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Don't plot small false positives that aren't text (remove noisy empty area)
            if w < 35 and h < 35:
                continue

            # extract the area we are looking for in this iteration from the screenshot
            text_block_cropped = screenshot[y : y + h, x : x + w]

            recognized_text = self.ocr.extract_text_from_image(text_block_cropped)[0]
            recognized_text = clean_string(recognized_text)
            recognized_texts.append(recognized_text)

            for recognized_text in recognized_texts:
                if search in recognized_text:
                    self.signals.log.emit(
                        f'"{search}" text found', LogService.LogType.DEFAULT
                    )
                    results[search] = (x, y)
                    return results

        return results

    def find_repair_tool_icon(self):
        """
        Find repair tool icon in the pet panel
        """

        screenshot_img = self.take_screenshot()
        templateMatch = cv2.matchTemplate(
            screenshot_img, self.repair_tools_icon_img, cv2.TM_CCOEFF_NORMED
        )
        matchLocations = np.where(templateMatch >= 0.9)
        reversed_match_locations = zip(*matchLocations[::-1])
        icon_position = next(
            (x for x in reversed_match_locations if x is not None), None
        )
        return icon_position

    def take_screenshot(self, left=0, top=0, right=1920, bottom=1080) -> cv2.Mat:
        """
        Take screenshot of an area. By default, take the whole focused screen.
        """

        # screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        # # convert Image to array with Numpy (to be processable with OpenCV), but we obtain an BGR image
        # screenshot = np.array(screenshot)
        # # switch back to RGB image
        # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        # return screenshot

        screenshot = self.wc.get_screenshot()
        cropped = screenshot[top:bottom, left:right]
        return cropped

    def compute_screenshot_size(self, x, y, h, w):
        left = x
        top = y
        right = x + w
        bottom = y + h
        return left, top, right, bottom

    def cast_throw_fish_bait(self):
        """
        Throw fish bait if possible.
        Create a countdown to the next cast.
        """

        now = datetime.datetime.now()
        if self.fish_bait_casted_at is None or now > self.fish_bait_casted_at:
            self.signals.log.emit(
                f"Cast bait ({self.options.cast_bait_key})", LogService.LogType.DEFAULT
            )
            keyboard.press_and_release(self.options.cast_bait_key)
            self.fish_bait_casted_at = now + datetime.timedelta(
                minutes=CAST_FISH_BAIT_COOLDOWN
            )
            # wait end of cast animation
            time.sleep(3)

    def check_and_repair_fishing_rod(self):
        # need_repair = is_fishing_rod_need_repair()
        need_repair = (
            self.usage_count_before_repair >= self.options.repair_strategy_repair_every
        )  # max_usage_before_repair
        if need_repair:
            self.repair_fishing_rod()
            time.sleep(1)
            self.usage_count_before_repair = 0  # reset count
            x, y = self.last_mouse_position
            mouse.move(x, y)
            time.sleep(1.5)

    def repair_fishing_rod(self):
        # open pet panel
        keyboard.press_and_release("alt+p")
        # wait panel to open
        time.sleep(1)

        x, y = self.find_repair_tool_icon()

        # move mouse to icon position then click on icon
        mouse.move(x + 5, y + 5, 300)
        time.sleep(0.3)
        mouse.click()
        # wait panel to open
        time.sleep(1)

        try:
            # detect 'repair all' button position then click
            # left, top, right, bottom = compute_screenshot_size(560, 540, 350, 800)
            screenshot = self.take_screenshot()
            results = self.extract_text_from_screenshot(screenshot, "Tout réparer")
            x, y = results["Tout réparer"]
            mouse.move(x, y)
            time.sleep(0.3)
            mouse.click()
            time.sleep(1)

            # detect on confirm modal the 'OK' button position then click
            # left, top, right, bottom = compute_screenshot_size(560, 540, 350, 800)
            screenshot = self.take_screenshot()
            results = self.extract_text_from_screenshot(screenshot, "OK")
            x, y = results["OK"]
            mouse.move(x, y)
            time.sleep(0.3)
            mouse.click()
            time.sleep(1)
        except:  # noqa: E722
            # Text recognition failed. We keep going.
            pass

        # exit tool panel
        keyboard.press_and_release("esc")
        time.sleep(2)
        # exit pet panel
        keyboard.press_and_release("esc")

    def switch_fishing_rod(self):
        if self.options.fishing_strategy is FishingStrategy.SINGLE_ROD:
            return

        self.signals.log.emit("Switch rod", LogService.LogType.DEFAULT)
        # open inventory
        keyboard.press_and_release("i")
        time.sleep(0.5)
        screenshot = self.take_screenshot()
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        # x, y is the center of the fishing rod icon in the inventory
        x = 0
        y = 0
        # switch to fishing rod dedicated to minigame
        if (
            self.current_equiped_fishing_rod.rarity
            is self.options.fishing_strategy_rod_to_fish.rarity
        ):
            matchLocations, resizedWidth, resizedHeight = cv2utils.match_template_scale(
                gray_screenshot,
                self.options.fishing_strategy_rod_to_play_minigame.img_gray,
            )
            for point in zip(*matchLocations[::-1]):
                if point is not None:
                    x = point[0] + (resizedWidth / 2)
                    y = point[1] + (resizedHeight / 2)
                    self.signals.log.emit(
                        f"Switch to mini game rod at ({x}, {y})",
                        LogService.LogType.INFO,
                    )
                    break
            self.current_equiped_fishing_rod = (
                self.options.fishing_strategy_rod_to_play_minigame
            )

        # switch to fishing rod dedicated to fish
        if (
            self.current_equiped_fishing_rod.rarity
            is self.options.fishing_strategy_rod_to_play_minigame.rarity
        ):
            matchLocations, resizedWidth, resizedHeight = cv2utils.match_template_scale(
                gray_screenshot, self.options.fishing_strategy_rod_to_fish.img_gray
            )
            for point in zip(*matchLocations[::-1]):
                if point is not None:
                    x = point[0] + (resizedWidth / 2)
                    y = point[1] + (resizedHeight / 2)
                    self.signals.log.emit(
                        f"Switch to fish rod at ({x}, {y})", LogService.LogType.INFO
                    )
                    break
            self.current_equiped_fishing_rod = self.options.fishing_strategy_rod_to_fish

        mouse.move(x, y)
        time.sleep(0.5)
        mouse.right_click()
        time.sleep(0.5)
        keyboard.press_and_release("esc")

    def has_vital_energy(self):
        screenshot_img = self.take_screenshot(760, 880, 1160, 980)

        # search for icon location
        templateMatch = cv2.matchTemplate(
            screenshot_img, self.vital_energy_icon_img, cv2.TM_CCOEFF_NORMED
        )
        matchLocations = np.where(templateMatch >= 0.8)

        icon_position = None
        for match in zip(*matchLocations[::-1]):
            if match is not None:
                icon_position = match
                break

        if icon_position is None:
            raise Exception("No icon detected")

        x, y = icon_position
        vital_energy_bar = screenshot_img[y : y + 15, x : x + 145]

        # create a mask to show only digit values
        hsv = cv2.cvtColor(vital_energy_bar, cv2.COLOR_BGR2HSV)
        sensitivity = 110
        hsv_lower = np.array([0, 0, 255 - sensitivity])
        hsv_upper = np.array([255, sensitivity, 255])
        mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

        texts: list[str] = []

        # to manipulate the orientation of dilution, large x means horizonatally dilating  more,
        # large y means vertically dilating more
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 24))
        # dilate, more the iteration more the dilation
        dilated = cv2.dilate(mask, kernel)

        # findContours returns 3 variables for getting contours
        contours, hierarchy = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Don't plot small false positives that aren't text (remove noisy empty area)
            if w < 35 and h < 35:
                continue

            text_block_cropped = vital_energy_bar[y : y + h, x : x + w]

            recognized_text = self.ocr.extract_text_from_image(text_block_cropped)[0]
            cleaned_recognized_text = clean_string(recognized_text)
            if cleaned_recognized_text != "":
                texts.append(cleaned_recognized_text)

        if len(texts) == 0:
            raise Exception("Vital energy value not recognized")

        current, max = texts[0].split("/")
        self.signals.log.emit(
            f"Current vital energy {current}/{max}", LogService.LogType.INFO
        )

        return int(current) > WORK_ENERGY_REQUIRED_FOR_FISHING

    def has_work_energy(self):
        return self.current_work_energy - WORK_ENERGY_REQUIRED_FOR_FISHING >= 0

    def update_work_energy(self):
        self.current_work_energy = (
            self.current_work_energy - WORK_ENERGY_REQUIRED_FOR_FISHING
        )

    def is_fish_hooked(self):
        screenshot_img = self.take_screenshot(860, 440, 1060, 640)
        # cv2.imwrite("screenshot.jpg", screenshot_img)
        # cv2.imshow("img", screenshot_img)
        hsv = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2HSV)
        hsv_lower = np.array([0, 0, 187])
        hsv_upper = np.array([77, 255, 255])
        mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
        templateMatch = cv2.matchTemplate(
            mask, self.hook_mark_img, cv2.TM_CCOEFF_NORMED
        )
        matchLocations = np.where(templateMatch >= 0.8)

        for point in zip(*matchLocations[::-1]):
            if point is not None:
                self.signals.log.emit("Fish hooked", LogService.LogType.INFO)
                return True

        return False

    def is_fishing_net_ready(self):
        """
        Detect if fishing mini game is ready
        """

        # when ready, the icon will appear on the middle of the screen so we take
        # a screenshot 400x400 of the middle of the screen to check
        left, top, right, bottom = self.compute_screenshot_size(860, 540, 200, 200)
        screenshot_img = self.take_screenshot(left, top, right, bottom)
        template_match = cv2.matchTemplate(
            screenshot_img, self.fishing_mini_game_ready_icon_img, cv2.TM_CCOEFF_NORMED
        )
        match_locations = np.where(template_match >= 0.9)

        for axis in zip(*match_locations[::-1]):
            if axis is not None:
                self.signals.log.emit("Fishing net ready", LogService.LogType.INFO)
                return True

        return False

    def get_lure_mini_game_y_position(self, hsv_screenshot_img) -> int:
        # purple color lower/upper
        # lure_hsv_lower = np.array([0, 255, 0])
        # lure_hsv_upper = np.array([7, 255, 255])
        lure_hsv_lower = np.array([120, 255, 0])
        lure_hsv_upper = np.array([127, 255, 255])

        lure_mask = cv2.inRange(hsv_screenshot_img, lure_hsv_lower, lure_hsv_upper)

        # to manipulate the orientation of dilution, large x means horizonatally dilating  more,
        # large y means vertically dilating more
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (12, 12))
        # dilate, more the iteration more the dilation
        dilated = cv2.dilate(lure_mask, kernel)

        # findContours returns 3 variables for getting contours
        contours, hierarchy = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        first_contour = contours[0] if len(contours) > 0 else None

        if first_contour is not None:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(first_contour)
            return y

        return 0

    def get_mini_game_zone_position(self, hsv_screenshot_img, hsv_lower, hsv_upper):
        hsv_lower = np.array(hsv_lower)
        hsv_upper = np.array(hsv_upper)
        zone_mask = cv2.inRange(hsv_screenshot_img, hsv_lower, hsv_upper)

        # to manipulate the orientation of dilution, large x means horizonatally dilating more,
        # large y means vertically dilating more
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 3))
        # dilate, more the iteration more the dilation
        dilated = cv2.dilate(zone_mask, kernel)

        # findContours returns 3 variables for getting contours
        contours, hierarchy = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        first_contour = contours[0] if len(contours) > 0 else None

        if first_contour is not None:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(first_contour)
            # y low zone (close to top screen), y mid zone, y high zone (close to bottom screen)
            return y, y + int(h / 2), y + h

        return 0, 0, 0

    def play_mini_game(self):
        # throw fishing net
        keyboard.press_and_release(self.options.cast_fishing_net_key)

        # throw net animation 2s + 5s before mini game starts
        now = datetime.datetime.now()
        starts_at = now + datetime.timedelta(seconds=7)

        # wait until mini game starts
        while starts_at > datetime.datetime.now():
            time.sleep(0.5)

        self.signals.log.emit("Mini game starts !", LogService.LogType.INFO)
        screenshot_img = self.take_screenshot(500, 100, 550, 560)
        hsv_img = cv2.cvtColor(screenshot_img, cv2.COLOR_RGB2HSV)
        hsv_lower = (
            YELLOW_ZONE_HSV_LOWER
            if self.options.focus_zone is FishingFocusZone.YELLOW
            else ORANGE_ZONE_HSV_LOWER
        )
        hsv_upper = (
            YELLOW_ZONE_HSV_UPPER
            if self.options.focus_zone is FishingFocusZone.YELLOW
            else ORANGE_ZONE_HSV_UPPER
        )
        y_low_zone, y_mid_zone, y_high_zone = self.get_mini_game_zone_position(
            hsv_img, hsv_lower, hsv_upper
        )
        self.signals.log.emit(
            f"{self.options.focus_zone.name} zone low/mid/high: {y_low_zone}/{y_mid_zone}/{y_high_zone}",
            LogService.LogType.INFO,
        )
        mini_game_ends_at = datetime.datetime.now() + datetime.timedelta(seconds=5)

        while mini_game_ends_at > datetime.datetime.now():
            screenshot_img = self.take_screenshot(500, 100, 550, 560)
            hsv_img = cv2.cvtColor(screenshot_img, cv2.COLOR_RGB2HSV)
            y_lure = self.get_lure_mini_game_y_position(hsv_img)
            self.signals.log.emit(f"y lure: {y_lure}", LogService.LogType.DEFAULT)
            if y_lure >= y_mid_zone:
                self.signals.log.emit("# Middle zone", LogService.LogType.DEFAULT)
                self.signals.log.emit("Press Space", LogService.LogType.DEFAULT)
                keyboard.press_and_release("space")
                # time.sleep(0.15)

        self.signals.log.emit("Mini game ended", LogService.LogType.INFO)
        time.sleep(5)
