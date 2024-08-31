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
        self.loop_timeout_sec = 30

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
        logging.debug(f"verify_code_pos: {verify_code_pos}")

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
            url = "https://ocr-api.vw.com/ocr"
            files = {
                'image': ('verify_code.png', img_byte_arr, 'image/png')
            }

            response = requests.post(url, files=files, verify=False)
            logging.debug(f"API response: {response.text}")

            verify_code_text = None
            if response.status_code == 200:
                response_data = response.json()
                if 'recognized_text' in response_data:
                    verify_code_text = response_data['recognized_text']
                    logging.debug(f"Recognized verify code: {verify_code_text}")
                else:
                    logging.warning("No text recognized in the response")
                    return False
            else:
                logging.error(f"Failed to call OCR API: {response.status_code}")
                return False

            if verify_code_text:
                self._send_key("{BACKSPACE}", clicks=5)
                self._send_key(verify_code_text)
                self._send_key("{ENTER}")
            else:
                logging.warning("No text recognized")
                return False

            msg_complete_verify_code_pos = imagesearch("photo/msg_complete_verify_code.bmp", precision=0.9)
            if msg_complete_verify_code_pos[0] != -1:
                self._send_key("{SPACE}")
                logging.info("Verify code completed")
                return True
            else:
                logging.warning("Verify code not completed")
                self._send_key("{SPACE}")
                return False
        else:
            logging.debug("No verify code needed")
            return True

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
        start_time = time.time()
        while True:
            if time.time() - start_time > self.loop_timeout_sec:
                logging.debug("Timeout reached, exiting loop.")
                break
            player_in_unknow_map_pos = imagesearch("photo/player_in_home_map.bmp", precision=0.92)
            if player_in_unknow_map_pos[0] == -1:
                break
            time.sleep(0.5)

        self._send_key("{SPACE}", clicks=2)

    def _enter_fire_lake_mission(self, check_image_path):
        logging.info("enter fire lake mission")
        start_time = time.time()
        while True:
            if time.time() - start_time > self.loop_timeout_sec:
                logging.debug("Timeout reached, exiting loop.")
                break

            npc_fire_lake_pos = imagesearch("photo/npc_fire_lake.bmp", precision=0.92)
            if npc_fire_lake_pos[0] != -1:
                logging.info("enter fire lake mission")
                while True:
                    logging.debug("right click npc fire lake")
                    self._mouse_click(npc_fire_lake_pos[0]+50, npc_fire_lake_pos[1]+50, button="right", clicks=2)
                    msg_fire_lake_npc_create_pos = imagesearch("photo/npc_confirm_or_cancel.bmp", precision=0.92)
                    if msg_fire_lake_npc_create_pos[0] != -1:
                        break
                self._send_key("{SPACE}")

            else:
                logging.info("no fire lake npc and try to move")
                npc_ghost_captain_pos = imagesearch("photo/npc_ghost_captain.bmp", precision=0.92)
                if npc_ghost_captain_pos[0] != -1:
                    self._mouse_click(npc_ghost_captain_pos[0]-20, npc_ghost_captain_pos[1], button="left", clicks=1)
                    self._send_key("{SPACE}")

            time.sleep(1)
            player_in_fire_lake_map_pos = imagesearch(check_image_path, precision=0.92)
            if player_in_fire_lake_map_pos[0] != -1:
                break

    def _tp_to_map(self):
        start_time = time.time()
        while True:
            if time.time() - start_time > self.loop_timeout_sec:
                logging.debug("Timeout reached, exiting loop.")
                break
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

    def make_money(self):
        """ this script is used to make money in the game
        1. check if player is in the money map
        2. if not, go to the money map
        3. if yes, execute skill to kill the monster
        """

        def quick_sell_item(shop_pos):
            logging.info("quick sell item")
            self._mouse_click(shop_pos[0], shop_pos[1], button="right", clicks=2)
            self._send_key("{DOWN}", clicks=8)
            self._send_key("{SPACE}")
            self._send_key("{DOWN}")
            self._send_key("{SPACE}", clicks=2)

        def buy_cheque(shop_pos):
            # npc_shop_pos[0]+50, npc_shop_pos[1]+50
            logging.info("start to buy heque")
            self._mouse_click(shop_pos[0], shop_pos[1], button="right", clicks=2)
            self._send_key("{DOWN}")
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
                start_time = time.time()
                while True:
                    if time.time() - start_time > self.loop_timeout_sec:
                        logging.debug("Timeout reached, exiting loop.")
                        break

                    shop_buy_or_cancel_button_pos = imagesearch("photo/shop_buy_or_cancel_button.bmp", precision=0.92)
                    logging.debug(f"shop_buy_or_cancel_button_pos: {shop_buy_or_cancel_button_pos}")
                    if shop_buy_or_cancel_button_pos[0] == -1:
                        break
                    self._mouse_click(shop_buy_or_cancel_button_pos[0]+10, shop_buy_or_cancel_button_pos[1]+10, button="left")
                    time.sleep(0.3)

        npc_shop_pos = imagesearch("photo/npc_shop.bmp", precision=0.92)
        if npc_shop_pos[0] != -1:
            npc_shop_pos = (npc_shop_pos[0]+50, npc_shop_pos[1]+50)

            quick_sell_item(npc_shop_pos)
            buy_cheque(npc_shop_pos)

            logging.info("tp to money map")
            self._tp_to_map()

            player_in_unknow_map_pos = imagesearch("photo/player_in_home_map.bmp", precision=0.92)
            if player_in_unknow_map_pos[0] == -1:

                start_time = time.time()
                while True:
                    self._enable_auto_attack()

                    if time.time() - start_time > self.loop_timeout_sec:
                        logging.debug("Timeout reached, exiting loop.")
                        break
                    if self._check_verify_code_with_api():
                        break
        else:
            logging.debug("no shop bar")

        time.sleep(2)

    def enter_fire_lake_mission(self):
        """ this script is used to enter the fire lake mission
        1. check if there is a mission
        2. enter the mission
        """
        msg_fire_lake_pos = imagesearch("photo/msg_fire_lake.bmp", precision=0.92)
        player_tiler_in_unknow_map_pos = imagesearch("photo/player_tiler_in_unknow_map.bmp", precision=0.92)
        if msg_fire_lake_pos[0] != -1 and player_tiler_in_unknow_map_pos[0] != -1:
            self._enter_fire_lake_mission("photo/player_tiler_in_fire_lake_map.bmp")

    def make_fire_lake(self):
        """ this script is used to make the fire lake mission
        1. check if player is in the fire lake map
        2. if not, enter the mission
        3. if yes, execute skill to kill the monster
        """

        def execute_skill(skill_pos, times=1):
            # buff
            self._send_key("d")
            # fight
            skill_result = False
            while skill_result != True:
                for i in range(times):
                    self._send_key("w")
                    self._mouse_click(skill_pos[0], skill_pos[1], button="left")
                    time.sleep(0.3)
                for i in range(3):
                    if imagesearch(f"photo/player_msg_execute_skill_{i}.bmp", precision=0.9)[0] != -1:
                        skill_result = True
                        break

        def talk_to_monster(monster_pos):
            logging.info("talk to monster")
            start_time = time.time()
            while True:
                if time.time() - start_time > self.loop_timeout_sec:
                    logging.debug("Timeout reached, exiting loop.")
                    break

                self._mouse_click(monster_pos[0], monster_pos[1], button="right", clicks=2)
                time.sleep(0.5)
                msg_fire_lake_monster_talking_pos = imagesearch("photo/msg_fire_lake_monster_talking.bmp", precision=0.92)
                logging.debug(f"msg_fire_lake_monster_talking_pos: {msg_fire_lake_monster_talking_pos}")
                if msg_fire_lake_monster_talking_pos[0] != -1:
                    break

            self._send_key("{SPACE}", clicks=2)
            time.sleep(0.3)

            start_time = time.time()
            while True:
                if time.time() - start_time > self.loop_timeout_sec:
                    logging.debug("Timeout reached, exiting loop.")
                    break
                if self._check_verify_code_with_api():
                    break

        # check if player is in mission map
        player_C0per_in_unknow_map_pos = imagesearch("photo/player_C0per_in_unknow_map.bmp", precision=0.9)
        player_C0per_in_fire_lake_map_pos = imagesearch("photo/player_C0per_in_fire_lake_map.bmp", precision=0.9)
        logging.debug(f"player_C0per_in_unknow_map_pos: {player_C0per_in_unknow_map_pos}")
        logging.debug(f"player_C0per_in_fire_lake_map_pos: {player_C0per_in_fire_lake_map_pos}")
        if player_C0per_in_unknow_map_pos[0] != -1:
            # not in the fire lake map
            # enter the mission
            self._enter_fire_lake_mission("photo/player_C0per_in_fire_lake_map.bmp")

        elif player_C0per_in_fire_lake_map_pos[0] != -1:
            # in the fire lake map
            # execute skill to kill the monster
            map_fire_lake_tower_pos = imagesearch("photo/map_fire_lake_tower_2.bmp", precision=0.7)
            if map_fire_lake_tower_pos[0] != -1:
                logging.info("execute skill to kill the monster")
                talk_to_monster((map_fire_lake_tower_pos[0]-200, map_fire_lake_tower_pos[1]+10))
                execute_skill((map_fire_lake_tower_pos[0]-180, map_fire_lake_tower_pos[1]+90), times=1)
            else:
                logging.debug("not in fire lake tower map")
        time.sleep(2)

    def make_soul(self):
        def _sell_soul():
            for i in range(1, 3):
                npc_pos = imagesearch(f"photo/npc_arms_soul_{i}.bmp", precision=0.92)
                if npc_pos[0] != -1:
                    npc_pos = (npc_pos[0]+50, npc_pos[1]+50)
                    self._mouse_click(npc_pos[0], npc_pos[1], button="right", clicks=2)
                    self._send_key("{SPACE}", clicks=6)

        player_in_home_map_pos = imagesearch("photo/player_in_home_map.bmp", precision=0.92)
        player_in_soul_map_pos = imagesearch("photo/player_in_soul_map.bmp", precision=0.92)
        if player_in_home_map_pos[0] != -1:
            _sell_soul()

            logging.info("tp to soul map")
            self._tp_to_map()

            player_in_soul_map_pos = imagesearch("photo/player_in_soul_map.bmp", precision=0.92)
            if player_in_soul_map_pos[0] != -1:
                start_time = time.time()
                while True:
                    self._enable_auto_attack()

                    if time.time() - start_time > self.loop_timeout_sec:
                        logging.debug("Timeout reached, exiting loop.")
                        break
                    if self._check_verify_code_with_api():
                        break
        elif player_in_soul_map_pos[0] != -1:
            logging.debug("in soul map")
            player_with_full_bag_pos = imagesearch("photo/player_with_full_bag.bmp", precision=0.92)
            if player_with_full_bag_pos[0] != -1:
                self._send_key("=")
                self._send_key("{SPACE}", clicks=4)
                self._send_key("-")
            else:
                logging.debug("no full bag")
        time.sleep(2)

    def enter_mission(self, map_name):
        target_pos = imagesearch(f"photo/npc_{map_name}.bmp", precision=0.92)
        player_tiler_in_unknow_map_pos = imagesearch("photo/player_tiler_in_unknow_map.bmp", precision=0.92)
        if target_pos[0] != -1 and player_tiler_in_unknow_map_pos[0] != -1:
            self._mouse_click(target_pos[0]+50, target_pos[1]+45, button="right", clicks=2)
            self._send_key("{SPACE}", clicks=2)
