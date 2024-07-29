import logging
import requests
import autoit
import time
import easyocr
import numpy as np
import torch

from io import BytesIO
from python_imagesearch.imagesearch import imagesearch
from PIL import ImageGrab

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Modifying the easyocr.Reader to use weights_only=True in torch.load
original_torch_load = torch.load


def patched_torch_load(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = True
    return original_torch_load(f, *args, **kwargs)


torch.load = patched_torch_load


class ROTask():
    def __init__(self, window_title, send_key_delay_time=350):
        self.window_title = window_title
        self.send_key_delay_time = send_key_delay_time  # ms
        autoit.win_activate(self.window_title)
        self.window_pos = autoit.win_get_pos(self.window_title)

    def _reset_mouse_pos(self):
        autoit.mouse_move(self.window_pos[0]+50, self.window_pos[1]+50, speed=1)

    def _mouse_click(self, x, y, button="left", clicks=1, delay_time=None):
        if delay_time is None:
            delay_time = self.send_key_delay_time
        autoit.mouse_move(x, y, speed=1)
        for i in range(clicks):
            time.sleep(delay_time / 1000)
            autoit.mouse_click(button)
        self._reset_mouse_pos()

    def _send_key(self, key, clicks=1, delay_time=None):
        if delay_time is None:
            delay_time = self.send_key_delay_time
        for i in range(clicks):
            time.sleep(delay_time / 1000)
            autoit.send(key)

    def _check_verify_code_with_api(self):
        logging.info("Starting verification code check.")

        verify_code_pos = imagesearch("photo/msg_verify_code.bmp", precision=0.9)
        logging.info(f"Image search result: {verify_code_pos}")

        if verify_code_pos[0] != -1:
            logging.info("Verify code needed")

            x, y = verify_code_pos
            logging.info(f"Verify code position: {x}, {y}")

            width = 35
            height = 20

            # Capture the image of the verification code area
            bbox = (x, y + 20, x + width, y + 20 + height)
            screenshot = ImageGrab.grab(bbox)
            logging.info(f"Screenshotted area: {bbox}")

            # Save the screenshot to a BytesIO object
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Send the image to the OCR API
            url = "http://100.105.149.4:5000/ocr"
            files = {
                'file': ('verify_code.png', img_byte_arr, 'image/png')
            }

            response = requests.post(url, files=files)
            logging.info(f"API response: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                if 'numbers_only' in response_data:
                    verify_code_text = response_data['numbers_only']
                    logging.info(f"Recognized verify code: {verify_code_text}")
                    self._send_key("{BACKSPACE}", clicks=5)
                    self._send_key(verify_code_text)
                    self._send_key("{ENTER}")
                else:
                    logging.warning("No text recognized in the response")
            else:
                logging.error(f"Failed to call OCR API: {response.status_code}")

    def _check_verify_code(self):
        logging.info("Starting verification code check.")

        verify_code_pos = imagesearch("photo/msg_verify_code.bmp", precision=0.9)
        logging.info(f"Image search result: {verify_code_pos}")

        if verify_code_pos[0] != -1:
            logging.info("Verify code needed")

            x, y = verify_code_pos
            logging.info(f"Verify code position: {x}, {y}")

            width = 30
            height = 15

            # Capture the image of the verification code area
            bbox = (x, y + 20, x + width, y + 20 + height)
            screenshot = ImageGrab.grab(bbox)
            logging.info(f"Screenshotted area: {bbox}")

            # Convert the image to grayscale
            gray_image = screenshot.convert('L')
            logging.info("Image converted to grayscale")

            # Convert the PIL image to a NumPy array
            gray_image_np = np.array(gray_image)
            logging.info("Image converted to NumPy array")

            # You can add other languages as needed, such as 'ch_sim' for Chinese recognition
            reader = easyocr.Reader(['en'])
            logging.info("Initialized EasyOCR reader")

            result = reader.readtext(gray_image_np)
            logging.info(f"OCR result: {result}")

            if result:
                verify_code_text = result[0][1]
                logging.info(f"Recognized verify code: {verify_code_text}")
                self._send_key(verify_code_text)
                self._send_key("{ENTER}")
            else:
                logging.warning("No text recognized")

    def make_money(self):
        """ this script is used to make money in the game
        1. check if player is in the money map
        2. if not, go to the money map
        3. if yes, execute skill to kill the monster
        """

        map_money_pos = imagesearch("photo/map_money.bmp", precision=0.92)
        if map_money_pos[0] == -1:
            logging.info("not in money map")

            # find the shop bar position
            npc_shop_pos = imagesearch("photo/npc_shop.bmp", precision=0.92)
            if npc_shop_pos[0] == -1:
                logging.info("no shop npc")
                return
            self._mouse_click(npc_shop_pos[0]+50, npc_shop_pos[1]+50, button="right", clicks=2)

            # sell all items
            self._send_key("{DOWN}", clicks=7)
            self._send_key("{SPACE}")
            self._send_key("{DOWN}")
            self._send_key("{SPACE}", clicks=2)

            # tp to make money map
            npc_tp_pos = imagesearch("photo/npc_tp.bmp", precision=0.92)
            if npc_tp_pos[0] == -1:
                logging.info("no tp npc")
                self._send_key("!1")
                return

            self._mouse_click(npc_tp_pos[0]+50, npc_tp_pos[1]+50, button="right", clicks=2)
            self._send_key("{SPACE}", clicks=3)
            time.sleep(2)

        else:
            logging.info("in money map")
            time.sleep(1)

        # if player not change position
        current_map_money_pos = imagesearch("photo/map_money.bmp", precision=1)
        if current_map_money_pos != -1:
            logging.info("player not change position")
            # boton
            self._send_key("!2")

            # check if there is a verify code
            self._check_verify_code_with_api()
            time.sleep(0.3)

            self._send_key("{SPACE}", clicks=2)

    def enter_fire_lake_mission(self):
        """ this script is used to enter the fire lake mission
        1. check if there is a mission
        2. enter the mission
        """

        # check if there is a mission
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        if msg_fire_lake_pos[0] == -1:
            logging.info("no mission msg")
            return

        # enter the mission
        npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
        if npc_fire_lake_pos[0] != -1:
            logging.info("enter fire lake mission")
            self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=2)
            self._send_key("{SPACE}")
        else:
            logging.info("no fire lake npc and try click the player hp")
            player_hp_pos = imagesearch("photo/player_hp.bmp", precision=0.92)
            self._mouse_click(player_hp_pos[0], player_hp_pos[1]+20, button="right")
            self._mouse_click(player_hp_pos[0]+20, player_hp_pos[1]+20, button="right")
            self._mouse_click(player_hp_pos[0]+40, player_hp_pos[1]+20, button="right")
            self._send_key("{SPACE}")
        time.sleep(1)

    def make_fire_lake_mission(self):
        """ this script is used to make the fire lake mission
        1. check if there is a verify code
        2. check if there is a mission
        3. check if player is in the fire lake map
        4. execute skill to kill the monster
        """

        self._check_verify_code_with_api()
        time.sleep(0.3)

        # check if there is a mission
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        if msg_fire_lake_pos[0] != -1:
            logging.info("already have fire lake mission")

        # check if player is in the fire lake map
        map_fire_lake_pos = imagesearch("photo/map_fire_lake.bmp", precision=0.92)
        if map_fire_lake_pos[0] == -1:
            # in the fire lake map
            # enter the mission
            npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
            if npc_fire_lake_pos[0] != -1:
                self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=2)
                self._send_key("{SPACE}")
                time.sleep(2)
            else:
                logging.info("no fire lake npc and try to move")
                player_hp_pos = imagesearch("photo/player_hp.bmp", precision=0.92)
                self._mouse_click(player_hp_pos[0]-10, player_hp_pos[1]+50, button="left")
                return
        else:
            # not in the fire lake map
            # execute skill to kill the monster
            map_fire_lake_tower_pos = imagesearch("photo/map_fire_lake_tower_2.bmp", precision=0.7)
            if map_fire_lake_tower_pos[0] != -1:
                self._send_key("d")
                for i in range(3):
                    self._send_key("w")
                    self._mouse_click(
                        map_fire_lake_tower_pos[0]-180,
                        map_fire_lake_tower_pos[1]+90,
                        button="left")
                    time.sleep(0.3)

                # talk to monster
                self._mouse_click(
                    map_fire_lake_tower_pos[0]-200,
                    map_fire_lake_tower_pos[1]+10,
                    button="right", clicks=2)
                time.sleep(0.3)
                self._send_key("{SPACE}", clicks=2)
                time.sleep(2)
            else:
                logging.info("not in fire lake tower map")
