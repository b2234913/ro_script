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

    def _mouse_left_drag(self, x1, y1, x2, y2):
        autoit.mouse_move(x1, y1, speed=20)
        time.sleep(0.5)
        autoit.mouse_down("left")
        time.sleep(0.5)
        autoit.mouse_move(x2, y2, speed=20)
        time.sleep(0.5)
        autoit.mouse_up("left")
        time.sleep(0.5)
        self._reset_mouse_pos()

    def _send_key(self, key, clicks=1, delay_time=None):
        if delay_time is None:
            delay_time = self.send_key_delay_time
        for i in range(clicks):
            time.sleep(delay_time / 1000)
            autoit.send(key)

    def _check_verify_code_with_api(self):

        verify_code_pos = imagesearch("photo/msg_verify_code.bmp", precision=0.9)
        logging.debug(f"Image search result: {verify_code_pos}")

        if verify_code_pos[0] != -1:
            logging.info("Verify code needed")

            x, y = verify_code_pos
            logging.debug(f"Verify code position: {x}, {y}")

            width = 35
            height = 20

            # Capture the image of the verification code area
            bbox = (x, y + 20, x + width, y + 20 + height)
            screenshot = ImageGrab.grab(bbox)
            logging.debug(f"Screenshotted area: {bbox}")

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
            logging.debug(f"API response: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                if 'numbers_only' in response_data:
                    verify_code_text = response_data['numbers_only']
                    logging.debug(f"Recognized verify code: {verify_code_text}")
                    self._send_key("{BACKSPACE}", clicks=5)
                    self._send_key(verify_code_text)
                    self._send_key("{ENTER}")
                    self._send_key("{SPACE}")
                else:
                    logging.warning("No text recognized in the response")
            else:
                logging.error(f"Failed to call OCR API: {response.status_code}")

    def _check_verify_code(self):
        logging.debug("Starting verification code check.")

        verify_code_pos = imagesearch("photo/msg_verify_code.bmp", precision=0.9)
        logging.debug(f"Image search result: {verify_code_pos}")

        if verify_code_pos[0] != -1:
            logging.debug("Verify code needed")

            x, y = verify_code_pos
            logging.debug(f"Verify code position: {x}, {y}")

            width = 30
            height = 15

            # Capture the image of the verification code area
            bbox = (x, y + 20, x + width, y + 20 + height)
            screenshot = ImageGrab.grab(bbox)
            logging.debug(f"Screenshotted area: {bbox}")

            # Convert the image to grayscale
            gray_image = screenshot.convert('L')
            logging.debug("Image converted to grayscale")

            # Convert the PIL image to a NumPy array
            gray_image_np = np.array(gray_image)
            logging.debug("Image converted to NumPy array")

            # You can add other languages as needed, such as 'ch_sim' for Chinese recognition
            reader = easyocr.Reader(['en'])
            logging.debug("Initialized EasyOCR reader")

            result = reader.readtext(gray_image_np)
            logging.debug(f"OCR result: {result}")

            if result:
                verify_code_text = result[0][1]
                logging.debug(f"Recognized verify code: {verify_code_text}")
                self._send_key(verify_code_text)
                self._send_key("{ENTER}")
            else:
                logging.warning("No text recognized")

    def _enable_auto_attack(self):
        logging.info("enable auto attack")
        self._send_key("=")
        while True:
            player_in_unknow_map_pos = imagesearch("photo/player_in_unknow_map.bmp", precision=0.92)
            if player_in_unknow_map_pos[0] != -1:
                break
            time.sleep(0.5)
        self._send_key("{SPACE}", clicks=2)

    def make_money(self):
        """ this script is used to make money in the game
        1. check if player is in the money map
        2. if not, go to the money map
        3. if yes, execute skill to kill the monster
        """

        def quick_sell_item(shop_pos):
            logging.info("quick sell item")
            self._mouse_click(shop_pos[0], shop_pos[1], button="right", clicks=2)
            self._send_key("{DOWN}", clicks=7)
            self._send_key("{SPACE}")
            self._send_key("{DOWN}")
            self._send_key("{SPACE}", clicks=2)

        def buy_cheque(shop_pos):
            # npc_shop_pos[0]+50, npc_shop_pos[1]+50
            logging.info("start to buy heque")
            self._mouse_click(shop_pos[0], shop_pos[1], button="right", clicks=2)
            self._send_key("{SPACE}")
            time.sleep(1)
            shop_item_heque_pos = imagesearch("photo/shop_item_heque.bmp", precision=0.92)
            shop_item_heque_blue_pos = imagesearch("photo/shop_item_heque_blue.bmp", precision=0.92)
            logging.debug(f"shop_item_heque_pos: {shop_item_heque_pos}")
            logging.debug(f"shop_item_heque_blue_pos: {shop_item_heque_blue_pos}")

            final_heque_pos = shop_item_heque_pos if shop_item_heque_pos[0] != -1 else shop_item_heque_blue_pos

            if final_heque_pos[0] != -1:
                logging.info("drag red packet into shopping cart")
                shop_shopping_cart_pos = imagesearch("photo/shop_shopping_cart.bmp", precision=0.92)
                logging.debug(f"shop_shopping_cart_pos: {shop_shopping_cart_pos}")

                for i in range(1):
                    self._mouse_left_drag(final_heque_pos[0]+10, final_heque_pos[1]+5,
                                          shop_shopping_cart_pos[0]+40, shop_shopping_cart_pos[1]+40)
                    self._send_key("{ENTER}")

                logging.info("confirm buy red packet")
                while True:
                    shop_buy_or_cancel_button_pos = imagesearch("photo/shop_buy_or_cancel_button.bmp", precision=0.92)
                    logging.debug(f"shop_buy_or_cancel_button_pos: {shop_buy_or_cancel_button_pos}")
                    if shop_buy_or_cancel_button_pos[0] == -1:
                        break
                    self._mouse_click(shop_buy_or_cancel_button_pos[0]+10, shop_buy_or_cancel_button_pos[1]+10, button="left")
                    time.sleep(0.3)

        def tp_to_money_map():
            while True:
                player_in_home_map_pos = imagesearch("photo/player_in_home_map.bmp", precision=0.92)
                if player_in_home_map_pos[0] == -1:
                    break
                npc_tp_pos = imagesearch("photo/npc_tp.bmp", precision=0.92)
                if npc_tp_pos[0] != -1:
                    npc_tp_pos = (npc_tp_pos[0]+70, npc_tp_pos[1]+50)
                    self._mouse_click(npc_tp_pos[0], npc_tp_pos[1], button="right", clicks=2)
                    self._send_key("{SPACE}", clicks=3)
                    time.sleep(2)
                else:
                    logging.error("no tp npc and run @load")
                    self._send_key("-")

        # find the shop bar position
        npc_shop_pos = imagesearch("photo/npc_shop.bmp", precision=0.92)
        if npc_shop_pos[0] != -1:
            npc_shop_pos = (npc_shop_pos[0]+50, npc_shop_pos[1]+50)

            quick_sell_item(npc_shop_pos)
            buy_cheque(npc_shop_pos)

            logging.info("tp to money map")

            tp_to_money_map()

            player_in_unknow_map_pos = imagesearch("photo/player_in_unknow_map.bmp", precision=0.92)
            if player_in_unknow_map_pos[0] != -1:
                self._enable_auto_attack()
                # check if there is a verify code
                self._check_verify_code_with_api()
        else:
            logging.debug("no shop bar")

        time.sleep(2)

    def enter_fire_lake_mission(self):
        """ this script is used to enter the fire lake mission
        1. check if there is a mission
        2. enter the mission
        """

        # check if there is a mission
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        if msg_fire_lake_pos[0] == -1:
            logging.debug("no mission msg")
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
            self._mouse_click(player_hp_pos[0]-15, player_hp_pos[1]+40, button="right", clicks=2)
            self._mouse_click(player_hp_pos[0]+30, player_hp_pos[1]+40, button="right", clicks=2)
            self._mouse_click(player_hp_pos[0]+50, player_hp_pos[1]+40, button="right", clicks=2)
            self._send_key("{SPACE}")
        time.sleep(1)

    def make_fire_lake_mission(self):
        """ this script is used to make the fire lake mission
        1. check if player is in the fire lake map
        2. if not, enter the mission
        3. if yes, execute skill to kill the monster
        """
        # check if player is in the fire lake map
        map_fire_lake_pos = imagesearch("photo/map_fire_lake.bmp", precision=0.95)
        if map_fire_lake_pos[0] == -1:
            # not in the fire lake map

            # enter the mission
            npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
            if npc_fire_lake_pos[0] != -1:
                logging.info("enter fire lake mission")
                self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=2)
                self._send_key("{SPACE}")
            else:
                logging.info("no fire lake npc and try click the player hp")
                player_hp_pos = imagesearch("photo/player_hp.bmp", precision=0.92)
                self._mouse_click(player_hp_pos[0]-15, player_hp_pos[1]+40, button="right", clicks=2)
                self._mouse_click(player_hp_pos[0]+30, player_hp_pos[1]+40, button="right", clicks=2)
                self._mouse_click(player_hp_pos[0]+50, player_hp_pos[1]+40, button="right", clicks=2)
                self._send_key("{SPACE}")
        else:
            # in the fire lake map

            # check if there is a verify code
            self._check_verify_code_with_api()
            time.sleep(0.3)

            # execute skill to kill the monster
            map_fire_lake_tower_pos = imagesearch("photo/map_fire_lake_tower_2.bmp", precision=0.7)
            if map_fire_lake_tower_pos[0] != -1:
                logging.info("execute skill to kill the monster")
                self._send_key("d")
                for i in range(1):
                    self._send_key("w")
                    self._mouse_click(
                        map_fire_lake_tower_pos[0]-180,
                        map_fire_lake_tower_pos[1]+90,
                        button="left")
                    time.sleep(0.3)

                # check if player is in the fire lake map
                map_fire_lake_pos = imagesearch("photo/map_fire_lake.bmp", precision=0.92)
                if map_fire_lake_pos != -1:
                    # talk to monster
                    logging.info("talk to monster")
                    self._mouse_click(
                        map_fire_lake_tower_pos[0]-200,
                        map_fire_lake_tower_pos[1]+10,
                        button="right", clicks=2)
                    time.sleep(0.3)
                    self._send_key("{SPACE}", clicks=2)
            else:
                logging.debug("not in fire lake tower map")
        time.sleep(2)
