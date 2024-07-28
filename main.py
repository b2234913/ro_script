import argparse
import keyboard
import os
import time
from ro_task import ROTask


def stop_script():
    # 立即终止 Python 解释器
    os._exit(0)


def main(task):
    ro_task = ROTask("Ragnarok")

    # 设置全局热键，当按下 Shift 键时调用 stop_script 函数
    keyboard.add_hotkey('shift', stop_script)

    if task == 'make_money':
        while True:
            ro_task.make_money()
            time.sleep(1)  # 添加延迟，防止过于频繁的任务调用
    elif task == 'enter_fire_lake':
        while True:
            ro_task.enter_fire_lake_mission()
            time.sleep(1)  # 添加延迟，防止过于频繁的任务调用
    elif task == 'make_fire_lake_mission':
        while True:
            ro_task.make_fire_lake_mission()
            time.sleep(1)  # 添加延迟，防止过于频繁的任务调用
    else:
        print("Unknown task. Available tasks are: make_money, enter_fire_lake, make_fire_lake_mission")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute different tasks for the Ragnarok game.")
    parser.add_argument(
        '-t', '--task',
        choices=['make_money', 'enter_fire_lake', 'make_fire_lake_mission'],
        required=True,
        help="The task to execute"
    )

    args = parser.parse_args()
    main(args.task)
