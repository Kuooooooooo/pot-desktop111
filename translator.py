import win32gui
import win32con
import requests
from pynput import keyboard
import time
from typing import Optional
import json
import os

class Translator:
    def __init__(self):
        """初始化翻译器"""
        self.ctrl_pressed = False
        self.win_pressed = False
        self.t_pressed = False
        self.last_translation_time = 0
        
        # 加载配置
        self.config = self.load_config()
        if not self.config:
            print("请先配置翻译API密钥")
            return
            
        print("✓ 翻译器初始化完成")
        print("等待快捷键触发 (Ctrl+Win+T)...")

    def load_config(self) -> dict:
        """加载配置文件"""
        try:
            config_path = "translator_config.json"
            if not os.path.exists(config_path):
                # 创建默认配置
                config = {
                    "api_type": "deepl",  # deepl, google, microsoft
                    "api_key": "",  # 需要填写API密钥
                    "source_lang": "auto",
                    "target_lang": "EN",
                }
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                print(f"已创建配置文件模板: {config_path}")
                print("请填写API密钥后重启程序")
                return None
                
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def get_window_text(self, hwnd) -> str:
        """获取窗口文本"""
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length == 0:
                return ""
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            text = buffer[:length].tobytes().decode('utf-16')
            return text
        except Exception as e:
            print(f"获取文本错误: {e}")
            return ""

    def set_window_text(self, hwnd, text: str) -> bool:
        """设置窗口文本"""
        try:
            result = win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
            return result != 0
        except Exception as e:
            print(f"设置文本错误: {e}")
            return False

    def translate_text(self, text: str) -> Optional[str]:
        """翻译文本"""
        if not text.strip():
            return None
            
        try:
            # 使用Google Translate API
            response = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={
                    "client": "gtx",
                    "sl": self.config["source_lang"],
                    "tl": self.config["target_lang"],
                    "dt": "t",
                    "q": text
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = ''.join([item[0] for item in result[0] if item[0]])
                return translated
            else:
                print(f"翻译请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
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
            # 获取当前窗口
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
        if not self.config:
            return
            
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()

def main():
    translator = Translator()
    translator.run()

if __name__ == "__main__":
    main() 