"""
桌面截图问答程序 - UI自动化操作元宝版

用法：
  1. 打开元宝并登录
  2. 运行: python screen_ask.py
  3. 程序自动截屏并发送到元宝，你在元宝里看回复
"""
import pyautogui
import win32gui
import win32con
import win32clipboard
import io
import time
import sys
from PIL import Image


class YuanbaoBot:
    def __init__(self):
        self.hwnd = None
        self.find_window()

    def find_window(self):
        """查找元宝窗口"""
        # 方法1: 按标题查找
        for title in ["元宝", "腾讯元宝", "Yuanbao"]:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                self.hwnd = hwnd
                break

        # 方法2: 按类名查找 EBWebView
        if not self.hwnd:
            for cls in ["Chrome_WidgetWin_0", "Chrome_WidgetWin_1", "WebViewWindowClass"]:
                hwnd = win32gui.FindWindow(cls, None)
                if hwnd:
                    title = win32gui.GetWindowText(hwnd)
                    if "元宝" in title or "yuanbao" in title.lower() or "hunyuan" in title.lower():
                        self.hwnd = hwnd
                        break

        # 方法3: 枚举所有窗口
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

        if self.hwnd:
            r = win32gui.GetWindowRect(self.hwnd)
            print(f"[✓] 找到元宝窗口: \"{win32gui.GetWindowText(self.hwnd)}\"")
            print(f"    位置: ({r[0]}, {r[1]})  {r[2]-r[0]}x{r[3]-r[1]}")
        else:
            print("[✗] 未找到元宝窗口！")

    def focus(self):
        """窗口置前"""
        if not self.hwnd:
            return False
        win32gui.SetForegroundWindow(self.hwnd)
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
        return True

    def get_rect(self):
        if not self.hwnd:
            return None
        r = win32gui.GetWindowRect(self.hwnd)
        return r[0], r[1], r[2] - r[0], r[3] - r[1]

    def copy_image_to_clipboard(self, image):
        """复制 PIL Image 到剪贴板"""
        output = io.BytesIO()
        image.convert("RGB").save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def click_input_area(self):
        """点击元宝底部输入框"""
        rect = self.get_rect()
        if not rect:
            return
        x, y, w, h = rect
        pyautogui.click(x + w // 2, y + h - 60)
        time.sleep(0.3)

    def send_screenshot(self, question=None):
        """截屏 → 粘贴到元宝 → 发送"""
        # 截屏
        print("[1/2] 正在截取当前屏幕...")
        screen = pyautogui.screenshot()
        ts = int(time.time())
        screen.save(f"screenshot_{ts}.png")
        print(f"    截图已保存 ({screen.size[0]}x{screen.size[1]})")

        # 发到元宝
        print("[2/2] 发送到元宝...")
        self.copy_image_to_clipboard(screen)
        self.focus()
        self.click_input_area()

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)

        if question:
            pyautogui.write(question, interval=0.02)
            time.sleep(0.3)

        pyautogui.press('enter')
        print("    已发送！请查看元宝窗口中的回复\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="桌面截图问答 - 自动截屏发到元宝")
    parser.add_argument("--question", "-q", default="请描述这张截图里有什么",
                        help="要问的问题")
    parser.add_argument("--delay", "-d", type=int, default=5,
                        help="倒计时秒数（默认5秒）")
    parser.add_argument("--quick", "-Q", action="store_true",
                        help="快速模式：不等待，立即截屏")
    args = parser.parse_args()

    bot = YuanbaoBot()
    if not bot.hwnd:
        print("\n未找到元宝窗口，请先启动元宝！")
        sys.exit(1)

    if not args.quick:
        print(f"倒计时 {args.delay} 秒，请切换到你要提问的界面...")
        for i in range(args.delay, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        print()

    bot.send_screenshot(args.question)


if __name__ == "__main__":
    main()
