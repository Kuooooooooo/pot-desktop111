import win32gui
import win32con
import win32api
import requests
from pynput import keyboard
import time
from typing import Optional

class PotTranslator:
    def __init__(self):
        """初始化翻译器"""
        self.ctrl_pressed = False
        self.win_pressed = False
        self.t_pressed = False
        self.last_translation_time = 0
        self.pot_port = 60828
        self.pot_url = f"http://127.0.0.1:{self.pot_port}"
        
        # 保存原始剪贴板内容
        self.original_clipboard = self.get_clipboard_text()
        
        # 测试Pot连接
        try:
            response = requests.post(f"{self.pot_url}/translate", 
                json={"text": "test", "from": "auto", "to": "en"},
                timeout=5
            )
            if response.status_code == 200:
                print("✓ Pot翻译服务已连接")
            else:
                print(f"✗ Pot服务响应异常: {response.status_code}")
        except Exception as e:
            print("✗ 连接Pot失败:", e)
            print("请确保Pot程序已启动")
        print("初始化完成，等待快捷键触发...")

    def get_clipboard_text(self) -> str:
        """获取剪贴板文本"""
        try:
            win32clipboard.OpenClipboard()
            try:
                return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                return ""
            finally:
                win32clipboard.CloseClipboard()
        except:
            return ""

    def set_clipboard_text(self, text: str):
        """设置剪贴板文本"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"设置剪贴板错误: {e}")

    def get_window_text(self, hwnd) -> str:
        """获取窗口文本"""
        try:
            # 获取文本长度
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length == 0:
                return ""
                
            # 分配缓冲区
            buffer = win32gui.PyMakeBuffer(length + 1)
            
            # 获取文本
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            
            # 转换为字符串
            text = buffer[:length].tobytes().decode('utf-16')
            print(f"获取到文本: {text}")
            return text
            
        except Exception as e:
            print(f"获取文本错误: {e}")
            return ""

    def set_window_text(self, hwnd, text: str) -> bool:
        """设置窗口文本"""
        try:
            # 直接发送文本设置消息
            result = win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
            return result != 0
        except Exception as e:
            print(f"设置文本错误: {e}")
            return False

    def translate_text(self, text: str) -> Optional[str]:
        """使用翻译API"""
        try:
            # 这里可以选择：
            # 1. Google Translate API
            # 2. DeepL API
            # 3. Microsoft Translator API
            # 具体使用哪个API，我们可以根据您的需求来选择
            
            # 示例：使用DeepL API
            response = requests.post(
                "https://api-free.deepl.com/v2/translate",
                headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                data={
                    "text": text,
                    "source_lang": "auto",
                    "target_lang": "EN"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["translations"][0]["text"]
            
            return None
        except Exception as e:
            print(f"翻译错误: {e}")
            return None

    def handle_translation(self):
        """处理翻译"""
        current_time = time.time()
        if current_time - self.last_translation_time < 1.0:
            return
        self.last_translation_time = current_time

        try:
            # 获取当前窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            print(f"\n当前窗口: {window_title}")

            # 获取文本
            text = self.get_window_text(hwnd)
            if not text:
                print("未获取到文本")
                return

            print(f"原文: {text}")
            
            # 翻译
            translated = self.translate_text(text)
            if not translated:
                print("翻译失败")
                return

            print(f"译文: {translated}")
            
            # 替换文本
            if self.set_window_text(hwnd, translated):
                print("✓ 文本替换成功")
            else:
                print("✗ 文本替换失败")

        except Exception as e:
            print(f"翻译处理错误: {e}")

    def on_press(self, key):
        """按键按下事件"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.cmd:
                self.win_pressed = True
            elif str(key) == "'t'" or str(key) == "'\\x14'":
                self.t_pressed = True

            if self.ctrl_pressed and self.win_pressed and self.t_pressed:
                print("检测到快捷键，开始翻译...")
                self.handle_translation()

        except AttributeError:
            pass

    def on_release(self, key):
        """按键释放事件"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.cmd:
                self.win_pressed = False
            elif str(key) == "'t'" or str(key) == "'\\x14'":
                self.t_pressed = False
        except AttributeError:
            pass

    def run(self):
        """运行翻译器"""
        print("Silent Translator is running... Press Ctrl+Win+T to translate")
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()

def main():
    translator = PotTranslator()
    translator.run()

if __name__ == "__main__":
    main() 