import time
import datetime
import mouse
import cv2
import keyboard
import numpy as np
from PIL import ImageGrab
import pytesseract
import pywinauto

from data.fishing.fishing_rod import FishingRodFactory, ItemRarity
import core.cv2utils as cv2utils

# Set tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'

# Code for when this file will become de startup file
# if __name__ == '__main__':
#     import sys
#     import app
#     sys.exit(app.run())

app_run = True

is_fishing = False

can_cast_fishing = True
hook_mark_img = cv2.imread(
    "assets/images/hook_mark.png", cv2.IMREAD_GRAYSCALE
)  # read and transform image to gray
repair_tools_icon_img = cv2.imread("assets/images/repair_tools_icon.jpg")
vital_energy_icon_img = cv2.imread("assets/images/vital_energy_icon.jpg")
fishing_mini_game_ready_icon_img = cv2.imread(
    "assets/images/fishing_mini_game_ready_icon.jpg"
)

CAST_FISHING_NET_KEY = "d"
CAST_FISH_LURE_KEY = "e"
CAST_FISH_BAIT_KEY = "r"
CAST_FISH_BAIT_COOLDOWN = 15  # 15min
fishBaitCastedAt = None

WORK_ENERGY_REQUIRED_FOR_FISHING = 60
current_work_energy = 8900

fishingRodList = FishingRodFactory()
FISHING_ROD_FOR_FISHING = fishingRodList.get(ItemRarity.RARE)
FISHING_ROD_FOR_MINI_GAME = fishingRodList.get(ItemRarity.EPIC)
current_equiped_fishing_rod = FISHING_ROD_FOR_FISHING

FISHING_TIMEOUT = 10  # seconds
FISHING_RETRY_MAX = 3  # number of retry if something goes wrong

# Temp
last_mouse_position = None
usage_count_before_repair = 0
max_usage_before_repair = 10


def debug(str):
    print("[{0}] {1}".format(datetime.datetime.now(), str))


def clean_string(text: str):
    return text.replace("\n", "").strip()


def is_game_stopped():
    global app_run

    stopped = True
    if stopped:
        app_run = False
        debug("Game crashed or disconnected")


def focus_LostArk_window():
    """
    Set focus on Lost Ark client window
    """

    app = pywinauto.application.Application()
    # LOST ARK (64-bit, DX11) v.2.12.2.1Shell_TrayWnd
    # find Lost Ark window
    handle = pywinauto.findwindows.find_windows(title_re="LOST ARK*")[0]
    # focus the window
    app.connect(handle=handle)
    window = app.window(handle=handle)
    window.set_focus()


def is_fishing_rod_need_repair():
    """
    Take screenshot of in-game chat area to check if the fishing rod needs to be repaired
    TODO: improve
    """

    chat_area_img = take_screenshot(0, 780, 700, 1080)

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

        recognized_text = pytesseract.image_to_string(text_block_cropped)

        if "Réparez" in recognized_text or "Reparez" in recognized_text:
            debug("Rod need to be repaired")
            return True

    return False


def extract_text_from_screenshot(
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

        recognized_text = pytesseract.image_to_string(text_block_cropped)
        recognized_text = clean_string(recognized_text)
        recognized_texts.append(recognized_text)

        for recognized_text in recognized_texts:
            if search in recognized_text:
                debug(f'"{search}" text found')
                results[search] = (x, y)
                return results

    return results


def find_repair_tool_icon():
    """
    Find repair tool icon in the pet panel
    """

    screenshot_img = take_screenshot()
    templateMatch = cv2.matchTemplate(
        screenshot_img, repair_tools_icon_img, cv2.TM_CCOEFF_NORMED
    )
    matchLocations = np.where(templateMatch >= 0.9)
    reversed_match_locations = zip(*matchLocations[::-1])
    icon_position = next((x for x in reversed_match_locations if x is not None), None)
    return icon_position


def take_screenshot(left=0, top=0, right=1920, bottom=1080) -> cv2.Mat:
    """
    Take screenshot of an area. By default, take the whole focused screen.
    """

    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    # convert Image to array with Numpy (to be processable with OpenCV), but we obtain an BGR image
    screenshot = np.array(screenshot)
    # switch back to RGB image
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    return screenshot


def compute_screenshot_size(x, y, h, w):
    left = x
    top = y
    right = x + w
    bottom = y + h
    return left, top, right, bottom


def cast_throw_fish_bait():
    """
    Throw fish bait if possible.
    Create a countdown to the next cast.
    """

    global fishBaitCastedAt
    now = datetime.datetime.now()
    if fishBaitCastedAt is None or now > fishBaitCastedAt:
        debug(f"Cast bait ({CAST_FISH_BAIT_KEY})")
        keyboard.press_and_release(CAST_FISH_BAIT_KEY)
        fishBaitCastedAt = now + datetime.timedelta(minutes=CAST_FISH_BAIT_COOLDOWN)
        # wait end of cast animation
        time.sleep(3)


def check_and_repair_fishing_rod():
    global usage_count_before_repair
    # need_repair = is_fishing_rod_need_repair()
    need_repair = usage_count_before_repair >= max_usage_before_repair
    if need_repair:
        repair_fishing_rod()
        time.sleep(1)
        usage_count_before_repair = 0  # reset count
        x, y = last_mouse_position
        mouse.move(x, y)
        time.sleep(1.5)


def repair_fishing_rod():
    # open pet panel
    keyboard.press_and_release("alt+p")
    # wait panel to open
    time.sleep(1)

    x, y = find_repair_tool_icon()

    # move mouse to icon position then click on icon
    mouse.move(x + 5, y + 5, 300)
    time.sleep(0.3)
    mouse.click()
    # wait panel to open
    time.sleep(1)

    # detect 'repair all' button position then click
    # left, top, right, bottom = compute_screenshot_size(560, 540, 350, 800)
    screenshot = take_screenshot()
    results = extract_text_from_screenshot(screenshot, "Tout réparer")
    x, y = results["Tout réparer"]
    mouse.move(x, y)
    time.sleep(0.3)
    mouse.click()
    time.sleep(1)

    # detect on confirm modal the 'OK' button position then click
    # left, top, right, bottom = compute_screenshot_size(560, 540, 350, 800)
    screenshot = take_screenshot()
    results = extract_text_from_screenshot(screenshot, "OK")
    x, y = results["OK"]
    mouse.move(x, y)
    time.sleep(0.3)
    mouse.click()
    time.sleep(1)

    # exit tool panel
    keyboard.press_and_release("esc")
    time.sleep(2)
    # exit pet panel
    keyboard.press_and_release("esc")


def switch_fishing_rod():
    global current_equiped_fishing_rod

    debug("Switch rod")
    # open inventory
    keyboard.press_and_release("i")
    time.sleep(0.5)
    screenshot = take_screenshot()
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    # x, y is the center of the fishing rod icon in the inventory
    x = 0
    y = 0
    # switch to fishing rod dedicated to minigame
    if current_equiped_fishing_rod.rarity is FISHING_ROD_FOR_FISHING.rarity:
        matchLocations, resizedWidth, resizedHeight = cv2utils.match_template_scale(
            gray_screenshot, FISHING_ROD_FOR_MINI_GAME.img_gray
        )
        for point in zip(*matchLocations[::-1]):
            if point is not None:
                x = point[0] + (resizedWidth / 2)
                y = point[1] + (resizedHeight / 2)
                debug(f"Switch to mini game rod at ({x}, {y})")
                break
        current_equiped_fishing_rod = FISHING_ROD_FOR_MINI_GAME

    # switch to fishing rod dedicated to fish
    if current_equiped_fishing_rod.rarity is FISHING_ROD_FOR_MINI_GAME.rarity:
        matchLocations, resizedWidth, resizedHeight = cv2utils.match_template_scale(
            gray_screenshot, FISHING_ROD_FOR_FISHING.img_gray
        )
        for point in zip(*matchLocations[::-1]):
            if point is not None:
                x = point[0] + (resizedWidth / 2)
                y = point[1] + (resizedHeight / 2)
                debug(f"Switch to fish rod at ({x}, {y})")
                break
        current_equiped_fishing_rod = FISHING_ROD_FOR_FISHING

    mouse.move(x, y)
    time.sleep(0.5)
    mouse.right_click()
    time.sleep(0.5)
    keyboard.press_and_release("esc")


def has_vital_energy():
    screenshot_img = take_screenshot(760, 880, 1160, 980)

    # search for icon location
    templateMatch = cv2.matchTemplate(
        screenshot_img, vital_energy_icon_img, cv2.TM_CCOEFF_NORMED
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

        recognized_text: str = pytesseract.image_to_string(text_block_cropped)
        cleaned_recognized_text = clean_string(recognized_text)
        if cleaned_recognized_text != "":
            texts.append(cleaned_recognized_text)

    if len(texts) == 0:
        raise Exception("Vital energy value not recognized")

    current, max = texts[0].split("/")
    debug(f"Current vital energy {current}/{max}")

    return int(current) > WORK_ENERGY_REQUIRED_FOR_FISHING


def has_work_energy():
    return current_work_energy - WORK_ENERGY_REQUIRED_FOR_FISHING >= 0


def update_work_energy():
    global current_work_energy
    current_work_energy = current_work_energy - WORK_ENERGY_REQUIRED_FOR_FISHING


def is_fish_hooked():
    screenshot_img = take_screenshot(860, 440, 1060, 640)
    hsv = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2HSV)
    hsv_lower = np.array([0, 0, 187])
    hsv_upper = np.array([77, 255, 255])
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    templateMatch = cv2.matchTemplate(mask, hook_mark_img, cv2.TM_CCOEFF_NORMED)
    matchLocations = np.where(templateMatch >= 0.8)

    for point in zip(*matchLocations[::-1]):
        if point is not None:
            debug("Hook mark detected")
            return True

    return False


def is_fishing_net_ready():
    """
    Detect if fishing mini game is ready
    """

    # when ready, the icon will appear on the middle of the screen so we take
    # a screenshot 400x400 of the middle of the screen to check
    left, top, right, bottom = compute_screenshot_size(860, 540, 200, 200)
    screenshot_img = take_screenshot(left, top, right, bottom)
    template_match = cv2.matchTemplate(
        screenshot_img, fishing_mini_game_ready_icon_img, cv2.TM_CCOEFF_NORMED
    )
    match_locations = np.where(template_match >= 0.9)

    for axis in zip(*match_locations[::-1]):
        if axis is not None:
            debug("Fishing net ready")
            return True

    return False


def get_lure_mini_game_y_position(hsv_screenshot_img) -> int:
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


def get_mini_game_zone_position(hsv_screenshot_img, hsv_lower, hsv_upper):
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


def play_mini_game():
    # throw net
    keyboard.press_and_release(CAST_FISHING_NET_KEY)

    # throw net animation 2s + 5s before mini game starts
    now = datetime.datetime.now()
    starts_at = now + datetime.timedelta(seconds=7)

    # wait until mini game starts
    while starts_at > datetime.datetime.now():
        time.sleep(0.5)

    debug("Mini game starts !")
    screenshot_img = take_screenshot(500, 100, 550, 560)
    hsv_img = cv2.cvtColor(screenshot_img, cv2.COLOR_RGB2HSV)
    # orange zone
    # perfect_zone_hsv_lower = np.array([106, 238, 176])
    # perfect_zone_hsv_upper = np.array([135, 255, 255])
    # yellow zone
    great_zone_hsv_lower = [21, 163, 189]
    great_zone_hsv_upper = [179, 255, 255]
    y_low_zone, y_mid_zone, y_high_zone = get_mini_game_zone_position(
        hsv_img, great_zone_hsv_lower, great_zone_hsv_upper
    )
    debug(f"Zone low/mid/high: {y_low_zone}/{y_mid_zone}/{y_high_zone}")
    mini_game_ends_at = datetime.datetime.now() + datetime.timedelta(seconds=5)

    while mini_game_ends_at > datetime.datetime.now():
        screenshot_img = take_screenshot(500, 100, 550, 560)
        hsv_img = cv2.cvtColor(screenshot_img, cv2.COLOR_RGB2HSV)
        y_lure = get_lure_mini_game_y_position(hsv_img)
        debug(f"y lure: {y_lure}")
        if y_lure >= y_mid_zone:
            debug("# Middle zone")
            debug("Press Space")
            keyboard.press_and_release("space")
            # time.sleep(0.15)

    debug("mini game done")
    time.sleep(5)


def run():
    global app_run, can_cast_fishing, last_mouse_position, usage_count_before_repair, is_fishing
    # focus_LostArk_window()

    last_mouse_position = mouse.get_position()

    while app_run:
        if is_fishing is False:
            try:
                can_fishing = has_work_energy()  # has_vital_energy()
                if can_fishing is False:
                    debug("Not enough energy")
                    app_run = False
            except Exception as ex:
                debug(
                    f"Vital energy parsing failed but keep app running. Error: {str(ex)}"
                )

        is_net_ready = is_fishing_net_ready()
        if is_net_ready:
            # switch to upgraded rod for easy mini game
            switch_fishing_rod()
            repair_fishing_rod()
            is_fishing = True
            x, y = last_mouse_position
            mouse.move(x, y, 300)
            time.sleep(1)
            play_mini_game()
            # switch back rod
            switch_fishing_rod()
            x, y = last_mouse_position
            mouse.move(x, y)
            time.sleep(1.5)
            is_fishing = False
            update_work_energy()
        else:
            if can_cast_fishing:
                check_and_repair_fishing_rod()
                cast_throw_fish_bait()
                update_work_energy()

                debug("Casting out lure")
                keyboard.press_and_release(CAST_FISH_LURE_KEY)
                can_cast_fishing = False
                is_fishing = True
                continue

            hooked = is_fish_hooked()
            if hooked:
                usage_count_before_repair += 1
                debug("Detected catch! Reeling in lure")
                keyboard.press_and_release(CAST_FISH_LURE_KEY)
                can_cast_fishing = True
                is_fishing = False
                time.sleep(6)

        time.sleep(0.005)


print("Fishing will be started in 5 seconds!")
time.sleep(5)
print("Started!")

run()

debug("App stopped")
