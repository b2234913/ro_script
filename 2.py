import ctypes
from ctypes import wintypes

# 定义回调函数类型
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)

# 定义回调函数


def enum_windows_callback(hwnd, lParam):
    windows = ctypes.cast(lParam, ctypes.POINTER(ctypes.py_object)).contents.value
    windows.append(hwnd)
    return True

# 列出所有窗口句柄


def list_windows():
    windows = []
    enum_windows_proc = WNDENUMPROC(enum_windows_callback)
    ctypes.windll.user32.EnumWindows(enum_windows_proc, ctypes.byref(ctypes.py_object(windows)))
    return windows

# 获取窗口标题


def get_window_title(hwnd):
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, title, length + 1)
    return title.value

# 获取所有标题为指定标题的窗口句柄


def get_windows_with_title(title):
    hwnds = list_windows()
    matching_hwnds = [hwnd for hwnd in hwnds if get_window_title(hwnd) == title]
    return matching_hwnds


# 主函数
if __name__ == "__main__":
    window_title = "Ragnarok"

    print(f"正在查找标题为 '{window_title}' 的窗口...")
    matching_hwnds = get_windows_with_title(window_title)

    if matching_hwnds:
        print(f"找到 {len(matching_hwnds)} 个匹配的窗口：")
        for hwnd in matching_hwnds:
            print(f"窗口句柄: {hwnd}")
    else:
        print(f"没有找到标题为 '{window_title}' 的窗口")
