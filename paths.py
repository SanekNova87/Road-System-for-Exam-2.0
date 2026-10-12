import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources", "media")

def find_image(keyword):
    if not os.path.isdir(RESOURCES_DIR):
        return None
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp"):
        pattern = os.path.join(RESOURCES_DIR, ext)
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath).lower()
            if keyword.lower() in filename:
                return filepath
    return None

ROAD = find_image("road")
CROSSROADS = find_image("crossroads") or find_image("cross")
CROSS_H = find_image("cross_h") or find_image("crossing")
PEDESTRIAN = find_image("pedestrian") or find_image("ped")
TL_RED = find_image("tl_red") or find_image("traffic") or find_image("light")
BLOCK = find_image("block") or find_image("sign")
START = find_image("start")
STOP = find_image("stop") or find_image("finish")
ICON = find_image("icon")

CAR_COLORS = ("red", "blue", "green", "yellow", "orange", "purple")

def car_image(color="red"):
    if color not in CAR_COLORS:
        color = "red"
    img = find_image("car_" + color)
    if img is None:
        img = find_image("car")
    return img

CAR_BOTTOM = car_image("red")

IMAGE_FILES = {
    "road": ROAD,
    "crossroads": CROSSROADS,
    "crossing": CROSS_H,
    "pedestrian": PEDESTRIAN,
    "traffic_light": TL_RED,
    "sign": BLOCK,
    "start": START,
    "stop": STOP,
    "car": CAR_BOTTOM,
}
