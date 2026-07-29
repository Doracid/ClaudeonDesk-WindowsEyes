"""
桌面截图问答 - 被 Clawd Electron 调用版
直接在目标目录，供 child_process.spawn 调用
"""
import pyautogui
import win32gui
import win32con
import win32clipboard
import io
import time
import sys
import argparse
from PIL import Image


class YuanbaoBot:
    def __init__(self):
        self.hwnd = None
        self.find_window()

    def find_window(self):
        for title in ["元宝", "腾讯元宝", "Yuanbao"]:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                self.hwnd = hwnd
                break
        if not self.hwnd:
            for cls in ["Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "WebViewWindowClass"]:
                hwnd = win32gui.FindWindow(cls, None)
                if hwnd:
                    t = win32gui.GetWindowText(hwnd)
                    if "元宝" in t or "yuanbao" in t.lower() or "hunyuan" in t.lower():
                        self.hwnd = hwnd
                        break
        if not self.hwnd:
            try:
                def enum_cb(hwnd, _):
                    t = win32gui.GetWindowText(hwnd)
                    if "元宝" in t or "yuanbao" in t.lower():
                        self.hwnd = hwnd
                        return False
                    return True
                win32gui.EnumWindows(enum_cb, None)
            except:
                pass

    def focus(self):
        if not self.hwnd:
            return False
        win32gui.SetForegroundWindow(self.hwnd)
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
        return True

    def set_clipboard_text(self, text):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()

    def copy_image_to_clipboard(self, image):
        output = io.BytesIO()
        image.convert("RGB").save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def click_input_area(self):
        if not self.hwnd:
            return
        r = win32gui.GetWindowRect(self.hwnd)
        pyautogui.click(r[0] + (r[2]-r[0]) // 2, r[3] - 60)
        time.sleep(0.3)

    def send_screenshot(self, question=None):
        screen = pyautogui.screenshot()
        full_text = "这是当前屏幕截图。右下角的小章鱼是桌宠程序，不用管它。" + (question or "")

        self.focus()
        self.click_input_area()

        # 先把文字复制到剪贴板 → 粘贴（绕过中文输入法）
        self.set_clipboard_text(full_text)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        # 再把图片复制到剪贴板 → 粘贴到同一条消息
        self.copy_image_to_clipboard(screen)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)

        # 发送
        pyautogui.press('enter')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", "-Q", action="store_true")
    parser.add_argument("--question", "-q", default="请描述这张截图里有什么")
    args = parser.parse_args()

    bot = YuanbaoBot()
    if not bot.hwnd:
        print("ERROR: 未找到元宝窗口")
        sys.exit(1)

    bot.send_screenshot(args.question)
    print("OK")


if __name__ == "__main__":
    main()
