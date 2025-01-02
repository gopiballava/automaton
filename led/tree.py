import requests
from typing import Optional

TREE_BASE_URL = "http://192.168.1.244/json/state"

LED_COUNT = 200

BLACK = [0, 0, 0]
RED = [255, 0, 0]
WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]

#'{"seg":{"i":["FF0000","00FF00","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","0000FF","ff00FF","000000"]}}'


def highlight_led(seq: Optional[int]):
    seg_list = []
    for i in range(LED_COUNT):
        seg_list.append(i)
        if i == seq:
            seg_list.append("0000FF")
        else:
            seg_list.append("000000")
    requests.post(
        url=TREE_BASE_URL,
        json={"seg": {"id": 1, "i": seg_list}},
    )
