from pynput import keyboard
import win32gui
import win32con
import requests
import time
from typing import Optional

class SilentTranslator:
    def __init__(self):
        """初始化翻译器"""
        self.api_url = "http://localhost:8080"  # Pot的默认API端口
        self.ctrl_pressed = False
        self.win_pressed = False
        self.t_pressed = False
        self.last_translation_time = 0  # 添加时间戳防止重复触发
        self.test_api_connection()  # 测试API连接
        print("初始化完成，等待快捷键触发...")
        
    def test_api_connection(self):
        """测试API连接"""
        try:
            # 增加更详细的连接测试信息
            print("正在测试API连接...")
            print(f"目标地址: {self.api_url}")
            
            response = requests.get(f"{self.api_url}/ping", timeout=5)  # 增加超时时间
            if response.status_code == 200:
                print("✓ API服务连接成功")
                print(f"响应内容: {response.text}")
                return True
            else:
                print(f"✗ API服务响应异常 (状态码: {response.status_code})")
                return False
        except requests.exceptions.ConnectTimeout:
            print("✗ 连接超时")
            print("请检查:")
            print("1. Pot程序是否已启动")
            print("2. 设置中的HTTP API服务是否已启用")
            print("3. API端口是否正确（默认8080）")
            return False
        except requests.exceptions.ConnectionError:
            print("✗ 连接被拒绝")
            print("请检查:")
            print("1. Pot的HTTP API服务是否已启用")
            print("2. 防火墙是否允许本地连接")
            print("3. 端口8080是否被其他程序占用")
            return False
        except Exception as e:
            print(f"✗ 其他错误: {str(e)}")
            return False
    
    def get_window_text(self, hwnd) -> str:
        """获取窗口文本"""
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            print(f"文本长度: {length}")
            if length == 0:
                return ""
                
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            text = buffer[:length].tobytes().decode('utf-16')
            print(f"获取到的文本: {text}")
            return text
        except Exception as e:
            print(f"获取文本错误: {e}")
            return ""
    
    def set_window_text(self, hwnd, text: str) -> bool:
        """设置窗口文本"""
        try:
            result = win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
            print(f"设置文本结果: {result}")
            return result
        except Exception as e:
            print(f"设置文本错误: {e}")
            return False
    
    def translate_text(self, text: str) -> Optional[str]:
        """调用翻译API"""
        try:
            print(f"正在翻译文本: {text}")
            response = requests.post(f"{self.api_url}/translate", json={
                "text": text,
                "from": "auto",
                "to": "zh"  # 改为中文，方便测试
            }, timeout=5)
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            if response.status_code == 200:
                return response.json()["result"]
            return None
        except Exception as e:
            print(f"翻译错误: {e}")
            return None
    
    def on_press(self, key):
        """按键按下事件"""
        try:
            print(f"按下按键: {key}")
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.cmd:  # Windows key
                self.win_pressed = True
            elif str(key) == "'t'" or str(key) == "'\\x14'":  # 添加对 \x14 的支持
                self.t_pressed = True
                
            # 检查组合键
            if self.ctrl_pressed and self.win_pressed and self.t_pressed:
                print("检测到快捷键组合，开始翻译...")
                self.handle_translation()
                
        except AttributeError as e:
            print(f"按键属性错误: {e}")
            pass

    def on_release(self, key):
        """按键释放事件"""
        try:
            print(f"释放按键: {key}")
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == keyboard.Key.cmd:
                self.win_pressed = False
            elif hasattr(key, 'char') and key.char == 't':
                self.t_pressed = False
        except AttributeError:
            pass
            
    def handle_translation(self):
        """处理翻译"""
        # 防止重复触发
        current_time = time.time()
        if current_time - self.last_translation_time < 1.0:  # 1秒内不重复触发
            return
        self.last_translation_time = current_time
        
        try:
            # 获取当前窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            print(f"\n当前窗口: {window_title} (句柄: {hwnd})")
            
            # 获取当前窗口文本
            text = self.get_window_text(hwnd)
            if not text:
                print("未获取到文本")
                return
                
            # 调用翻译
            translated = self.translate_text(text)
            if not translated:
                print("翻译失败")
                return
                
            print(f"翻译结果: {translated}")
            
            # 设置翻译后的文本
            if self.set_window_text(hwnd, translated):
                print("文本替换成功")
            else:
                print("文本替换失败")
            
        except Exception as e:
            print(f"翻译处理错误: {e}")
    
    def run(self):
        """运行翻译器"""
        print("Silent Translator is running... Press Ctrl+Win+T to translate")
        
        # 监听键盘事件
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()

def main():
    translator = SilentTranslator()
    translator.run()

if __name__ == "__main__":
    main() 