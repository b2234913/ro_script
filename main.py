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
            print(f"Error removing temporary directory: {e}")


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
    elif task == 'make_fire_lake_mission':
        while True:
            ro_task.make_fire_lake_mission()
            time.sleep(1)  # Add delay to prevent too frequent task calls
    else:
        print("Unknown task. Available tasks are: make_money, enter_fire_lake, make_fire_lake_mission")


if __name__ == "__main__":
    # Register the cleanup function to be called on program exit
    atexit.register(remove_meipass)

    parser = argparse.ArgumentParser(description="Execute different tasks for the Ragnarok game.")
    parser.add_argument(
        '-t', '--task',
        choices=['make_money', 'enter_fire_lake', 'make_fire_lake_mission'],
        required=True,
        help="The task to execute"
    )
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=500,
        help="The delay time (in milliseconds) for sending keys"
    )

    args = parser.parse_args()
    main(args.task, args.delay)
