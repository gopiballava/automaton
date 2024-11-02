from collections import deque
import requests
import time
import traceback
from typing import Dict, Tuple

SIGN_BASE_URL = "http://192.168.1.242/json/state"

# time curl -X POST "http://192.168.1.242/json/state" -H "Content-Type: application/json" -d '{"seg":{"i":[0,13,"0000",13,25,"FF0000",25,39,"0000FF",39,55,"FF00FF"]}}'
BLACK = [0, 0, 0]
RED = [255, 0, 0]
WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]

#'{"seg":{"i":["FF0000","00FF00","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","ff00FF","000000"]}}'
def gen_seg(offset: int):
    COLOR_LIST = deque(["FF0000", "00FF00", "0000FF", "FFFF00"])
    COLOR_LIST.rotate(offset)
    return {
        "seg": {
            "i": [
                0,
                13,
                COLOR_LIST[0],
                13,
                25,
                COLOR_LIST[1],
                25,
                39,
                COLOR_LIST[2],
                39,
                55,
                COLOR_LIST[3],
            ]
        }
    }


def gen_letters(letters: Dict[str, Tuple], default_color=BLACK):
    return {
        "bri": 255,
        "seg": {
            "i": [
                0,
                13,
                letters.get('h', default_color),
                13,
                25,
                letters.get('a', default_color),
                25,
                39,
                letters.get('r1', default_color),
                39,
                55,
                letters.get('r2', default_color),
            ]
        }
    }

def hello(offset: int = 0):
    requests.post(
        url=SIGN_BASE_URL,
        json=gen_seg(offset),
    )

def show_letters(letters: Dict[str, Tuple], default_color):
    requests.post(
        url=SIGN_BASE_URL,
        json=gen_letters(letters, default_color),
    )
    print(gen_letters(letters))

def send_command(cmd: Dict):
    backoff = 0.1
    for _ in range(10):
        try:
            requests.post(
                url=SIGN_BASE_URL,
                json=cmd,
                timeout=1,
            )
            return
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            traceback.print_exc()
            print("Retrying after delay")
            time.sleep(backoff)
            backoff = max(backoff * 2, 5)

def zoom_internal(target_color, default_color):
    LETTERS = ["h", "a", "r1", "r2"]
    FADE_LENGTH = 30
    for i in range(len(LETTERS)):
        for fade in range(FADE_LENGTH):
            # print(f"targert: {target_color}")
            print(f"i: {i} fade: {fade}")
            letters = {}
            if i>0:
                for letter in LETTERS[0:i]:
                    letters[letter] = target_color
            last_color = list(target_color)
            for k in range(len(last_color)):
                multiplier = fade/FADE_LENGTH 
                last_color[k] = int(multiplier * last_color[k] + ((1-multiplier) * default_color[k]))
            letters[LETTERS[i]] = last_color
            show_letters(letters, default_color)
            # time.sleep(0.01)

def zoom():
    zoom_internal([255, 0, 255], [0, 0, 0])
    zoom_internal([0, 255, 255], [255, 0, 255])
    zoom_internal([255, 255, 255], [0, 255, 255])


def usa():
    show_letters({"h": RED, "a": WHITE, "r1": BLUE}, BLACK)

H_LENGTH = 6
W_LENGTH = 4

def harris_walz(h, w, default=BLACK):
    if len(h) < H_LENGTH:
        h.extend([default] * (H_LENGTH - len(h)))
    if len(w) < W_LENGTH:
        w.extend([default] * (W_LENGTH - len(w)))
    cmd = {
        "bri": 255,
        "seg": {
            "i": [
                0, 13, h[0],  # H
                13, 25, h[1], # A
                25, 39, h[2], # R
                39, 53, h[3], # R
                53, 59, h[4], # I
                59, 71, h[5], # S

                71, 77, w[3], # Z
                77, 81, w[2], # L
                81, 88, w[1], # A
                88, 99, w[0], # W
            ]
        }
    }
    print(h)
    send_command(cmd)

def _fade_tuple(fraction, start, end) -> Tuple:
    retv = []
    for i in range(3):
        retv.append(int(start[i] * (1-fraction) + end[i] * fraction))
    return retv

def dual():
    # harris_walz([RED, GREEN, BLUE, WHITE, GREEN, BLUE], [BLUE, WHITE, GREEN, BLUE])
    FADE_LENGTH = 20
    AMERICA = [RED, WHITE, BLUE] * 3
    BG = [BLACK] * H_LENGTH
    WALZ = [_fade_tuple(0.3, WHITE, BLACK)] * W_LENGTH
    while True:
        for i in range(3):
            for j in range(H_LENGTH):
                for fade in range(FADE_LENGTH):
                    harris = [AMERICA[i]] * (1 + j) + BG
                    harris[j] = _fade_tuple(fade/FADE_LENGTH, BG[0], AMERICA[i])
                    harris_walz(harris, WALZ)

            for fade in range(FADE_LENGTH):
                old_walz = WALZ[0]
                WALZ = [_fade_tuple(fade/FADE_LENGTH, old_walz, AMERICA[i])] * W_LENGTH
                harris_walz(harris, WALZ)
            BG = [AMERICA[i]] * H_LENGTH
            # time.sleep(1)
    # for j in range(10):
    #     for i in range(3):
    #         harris_walz(AMERICA[i:], AMERICA[i:])
    #         time.sleep(0.5)
