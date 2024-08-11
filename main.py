import logging
import argparse
import keyboard
import os
import time
from ro_task import ROTask
import shutil
import atexit
import sys


def stop_script():
    # Immediately terminate the Python interpreter
    os._exit(0)


def remove_meipass():
    # sys._MEIPASS is set by PyInstaller to the path of the temporary directory
    if hasattr(sys, '_MEIPASS'):
        try:
            shutil.rmtree(sys._MEIPASS)
        except Exception as e:
            logging.error(f"Error removing temporary directory: {e}")


def main(task, send_key_delay_time):
    ro_task = ROTask("Ragnarok", send_key_delay_time)

    # Set a global hotkey, call stop_script function when the Shift key is pressed
    keyboard.add_hotkey('shift', stop_script)

    if task == 'make_money':
        while True:
            ro_task.make_money()
            time.sleep(1)  # Add delay to prevent too frequent task calls
    elif task == 'enter_fire_lake':
        while True:
            ro_task.enter_fire_lake_mission()
            time.sleep(1)  # Add delay to prevent too frequent task calls
    elif task == 'make_fire_lake':
        while True:
            ro_task.make_fire_lake()
            time.sleep(1)  # Add delay to prevent too frequent task calls
    elif task == 'enter_king_gym':
        while True:
            ro_task.enter_mission("king_gym")
            time.sleep(1)
    elif task == 'enter_bad_gym':
        while True:
            ro_task.enter_mission("bad_gym")
            time.sleep(1)
    else:
        logging.error("Unknown task. Available tasks are: make_money, enter_fire_lake, make_fire_lake")


if __name__ == "__main__":
    # Register the cleanup function to be called on program exit
    atexit.register(remove_meipass)

    parser = argparse.ArgumentParser(description="Execute different tasks for the Ragnarok game.")
    parser.add_argument(
        '-t', '--task',
        choices=['make_money', 'make_fire_lake', 'enter_fire_lake', 'enter_king_gym', 'enter_bad_gym'],
        required=True,
        help="The task to execute"
    )
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=350,
        help="The delay time (in milliseconds) for sending keys"
    )
    parser.add_argument(
        '-l', '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help="Set the logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set the logging level based on the argument
    logging.basicConfig(level=getattr(logging, args.log_level), format='%(asctime)s - %(levelname)s - %(message)s')

    main(args.task, args.delay)
