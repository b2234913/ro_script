import autoit
import time
import easyocr
import numpy as np

from python_imagesearch.imagesearch import imagesearch
from PIL import ImageGrab


class ROTask():
    def __init__(self, window_title):
        self.window_title = window_title
        autoit.win_activate(self.window_title)

    def _mouse_click(self, x, y, button="left", clicks=1, speed=10):
        autoit.mouse_move(x, y, speed)
        for i in range(clicks):
            autoit.mouse_click(button)

    def _send_key(self, key, clicks=1, speed=300):
        for i in range(clicks):
            time.sleep(speed / 1000)
            autoit.send(key)

    def _check_verify_code(self):
        verify_code_pos = imagesearch("photo/msg_verify_code.bmp", precision=0.9)
        if verify_code_pos[0] != -1:
            print("verify code needed")

            x, y = verify_code_pos

            print("Verify code position:", x, y)

            width = 30
            height = 15

            # 截取验证码区域的图像
            bbox = (x, y+20, x + width, y+20 + height)
            screenshot = ImageGrab.grab(bbox)

            # 将图像转换为灰阶
            gray_image = screenshot.convert('L')

            # 将 PIL 图像转换为 NumPy 数组
            gray_image_np = np.array(gray_image)

            # 使用 EasyOCR 识别验证码
            reader = easyocr.Reader(['en'])  # 可以根据需要添加其他语言，例如 'ch_sim' 进行中文识别
            result = reader.readtext(gray_image_np)

            if result:
                verify_code_text = result[0][1]
                print("Recognized verify code:", verify_code_text)
                self._send_key(verify_code_text, clicks=1)
                self._send_key("{ENTER}", clicks=1)
            else:
                print("No text recognized")

    def make_money(self):
        """ this script is used to make money in the game
        1. sell all items in the shop
        2. teleport to the map where can make money
        3. boton
        """

        # find the shop bar position
        npc_shop_pos = imagesearch("photo/npc_shop.bmp", precision=0.92)
        if npc_shop_pos[0] == -1:
            print("no shop npc")
            return

        self._mouse_click(npc_shop_pos[0]+50, npc_shop_pos[1]+50, button="right", clicks=1)

        # sell all items
        self._send_key("{DOWN}", clicks=7)
        self._send_key("{SPACE}", clicks=1)
        self._send_key("{DOWN}", clicks=1)
        self._send_key("{SPACE}", clicks=2)

        # tp to make money map
        npc_tp_pos = imagesearch("photo/npc_tp.bmp", precision=0.92)
        if npc_tp_pos[0] == -1:
            print("no tp npc")
            return

        self._mouse_click(npc_tp_pos[0]+50, npc_tp_pos[1]+50, button="right", clicks=1)
        self._send_key("{SPACE}", clicks=3)
        time.sleep(1.5)

        # boton
        self._send_key("!2", clicks=1)
        self._send_key("{SPACE}", clicks=2)

    def enter_fire_lake_mission(self):
        """ this script is used to enter the fire lake mission
        """

        # check if there is a mission
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        if msg_fire_lake_pos[0] == -1:
            print("no mission msg")
            return

        # enter the mission
        npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
        if npc_fire_lake_pos[0] == -1:
            print("no fire lake npc")
            return
        self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=1)
        self._send_key("{SPACE}", clicks=1)

    def make_fire_lake_mission(self):

        self._check_verify_code()
        time.sleep(0.3)

        # check if there is a mission
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        if msg_fire_lake_pos[0] != -1:
            print("already have fire lake mission")

        # check if player is in the fire lake map
        map_fire_lake_pos = imagesearch("photo/map_fire_lake.bmp", precision=0.92)
        if map_fire_lake_pos[0] == -1:
            # enter the mission
            npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
            self._send_key("d", clicks=1)
            if npc_fire_lake_pos[0] != -1:
                self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=1)
                self._send_key("{SPACE}", clicks=1)
                time.sleep(2)
            else:
                print("no fire lake npc and try to move")
                player_hp_pos = imagesearch("photo/player_hp.bmp", precision=0.92)
                self._mouse_click(player_hp_pos[0]-10, player_hp_pos[1]+50, button="left", clicks=1)
                return

        # execute skill to kill the monster
        map_fire_lake_tower_pos = imagesearch("photo/map_fire_lake_tower_2.bmp", precision=0.7)
        if map_fire_lake_tower_pos[0] != -1:
            for i in range(3):
                self._send_key("w", clicks=1)
                self._mouse_click(
                    map_fire_lake_tower_pos[0]-180,
                    map_fire_lake_tower_pos[1]+90,
                    button="left", clicks=1)
                time.sleep(0.3)

            # talk to monster
            self._mouse_click(
                map_fire_lake_tower_pos[0]-200,
                map_fire_lake_tower_pos[1]+10,
                button="right", clicks=1, speed=10)
            time.sleep(0.3)
            self._send_key("{SPACE}", clicks=2, speed=400)
            time.sleep(2)
        else:
            print("not in fire lake tower map")
