import win32gui
import win32con
import win32clipboard
import win32api
import win32ui
from ctypes import windll
import requests
from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
from typing import Optional

class WindowHandler:
    """窗口处理器基类"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return False
        
    def get_text(self, hwnd: int) -> str:
        """获取文本的默认实现"""
        try:
            # 直接使用Windows API获取文本
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = win32gui.PyMakeBuffer(length + 1)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                return buffer[:length].tobytes().decode('utf-16')
        except:
            pass
        return ""

    def set_text(self, hwnd: int, text: str) -> bool:
        """设置文本的默认实现"""
        try:
            return bool(win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text))
        except:
            return False

    def get_text_safely(self, hwnd: int) -> str:
        """安全地获取文本"""
        try:
            # 尝试直接获取文本
            text = self.get_text(hwnd)
            if text and text.strip():
                return text
                
            # 如果失败，使用剪贴板方法
            return self.get_text_by_clipboard(hwnd)
        except:
            return ""
            
    def get_text_by_clipboard(self, hwnd: int) -> str:
        """通过剪贴板获取文本"""
        original = None
        try:
            # 保存并清空剪贴板
            win32clipboard.OpenClipboard()
            try:
                original = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                pass
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)  # 增加延时
            
            # 模拟Ctrl+A
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.2)  # 增加延时
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 模拟Ctrl+C
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('C'), 0, 0, 0)
            time.sleep(0.2)  # 增加延时
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)  # 增加延时
            
            # 获取文本
            text = ""
            win32clipboard.OpenClipboard()
            try:
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            finally:
                win32clipboard.EmptyClipboard()
                if original:
                    try:
                        win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                    except:
                        pass
                win32clipboard.CloseClipboard()
            
            return text
            
        except Exception as e:
            print(f"剪贴板操作错误: {e}")
            if original:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                except:
                    pass
            return ""

    def set_text_by_clipboard(self, hwnd: int, text: str) -> bool:
        """通过剪贴板设置文本的基础实现"""
        try:
            # 保存原始剪贴板内容
            win32clipboard.OpenClipboard()
            try:
                original = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                original = None
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            
            # 设置新文本到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            
            # 模拟Ctrl+A和Ctrl+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 恢复原始剪贴板
            if original:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                
            return True
            
        except Exception as e:
            print(f"剪贴板设置文本错误: {e}")
            return False

class NotepadHandler(WindowHandler):
    """记事本处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return class_name == "Notepad"
        
    def get_text(self, hwnd: int) -> str:
        try:
            # 先尝试使用剪贴板方法
            text = self.get_text_by_clipboard(hwnd)
            if text and text.strip():
                print(f"通过剪贴板获取到文本: {text}")
                return text
                
            # 如果剪贴板方法失败，尝试直接获取
            edit_hwnd = win32gui.FindWindowEx(hwnd, 0, "Edit", None)
            if not edit_hwnd:
                print("未找到记事本编辑框")
                return ""
                
            # 获取文本长度
            length = win32gui.SendMessage(edit_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length == 0:
                print("记事本内容为空")
                return ""
                
            # 获取文本
            buffer = win32gui.PyMakeBuffer(length + 1)
            result = win32gui.SendMessage(edit_hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            if result:
                try:
                    # 先尝试UTF-16
                    text = buffer[:length].tobytes().decode('utf-16-le')
                    print(f"使用UTF-16-LE解码成功: {text}")
                    return text
                except:
                    try:
                        # 再尝试系统默认编码
                        text = buffer[:length].tobytes().decode()
                        print(f"使用系统默认编码解码成功: {text}")
                        return text
                    except:
                        print("所有解码方法都失败")
            else:
                print("获取记事本文本失败")
                
            return ""
            
        except Exception as e:
            print(f"获取记事本文本错误: {e}")
            return ""
            
    def set_text(self, hwnd: int, text: str) -> bool:
        try:
            # 先尝试使用剪贴板方法
            if self.set_text_by_clipboard(hwnd, text):
                print("使用剪贴板方法设置文本成功")
                return True
                
            # 如果剪贴板方法失败，尝试直接设置
            edit_hwnd = win32gui.FindWindowEx(hwnd, 0, "Edit", None)
            if not edit_hwnd:
                print("未找到记事本编辑框")
                return False
                
            # 设置文本
            result = win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, text)
            if result:
                print("直接设置文本成功")
                return True
            else:
                print("设置文本失败")
                return False
                
        except Exception as e:
            print(f"设置记事本文本错误: {e}")
            return False

class QQHandler(WindowHandler):
    """QQ窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return "TXGuiFoundation" in class_name
        
    def get_text(self, hwnd: int) -> str:
        try:
            # 查找QQ输入框
            edit_hwnd = win32gui.FindWindowEx(hwnd, 0, "QQEdit", None)
            if edit_hwnd:
                # 使用EM_GETTEXT消息
                length = win32gui.SendMessage(edit_hwnd, win32con.EM_GETTEXTLENGTH, 0, 0)
                buffer = win32gui.PyMakeBuffer(length + 1)
                win32gui.SendMessage(edit_hwnd, win32con.EM_GETTEXT, length + 1, buffer)
                return buffer[:length].tobytes().decode('utf-16')
        except:
            pass
        return super().get_text(hwnd)

    def set_text(self, hwnd: int, text: str) -> bool:
        try:
            edit_hwnd = win32gui.FindWindowEx(hwnd, 0, "QQEdit", None)
            if edit_hwnd:
                # 使用EM_SETTEXT消息
                return bool(win32gui.SendMessage(edit_hwnd, win32con.EM_SETTEXT, 0, text))
        except:
            pass
        return super().set_text(hwnd, text)

class DingTalkHandler(WindowHandler):
    """钉钉窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return "StandardFrame" in class_name or "DingTalk" in class_name
        
    def get_text(self, hwnd: int) -> str:
        # 钉钉使用标准Windows消息
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            return buffer[:length].tobytes().decode('utf-16')
        except:
            return ""

class WeChatHandler(WindowHandler):
    """微信窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return "WeChatMainWndForPC" in class_name
        
    def get_text(self, hwnd: int) -> str:
        try:
            # 检查窗口是否是微信主窗口
            if not win32gui.IsWindow(hwnd):
                print("无效的微信窗口")
                return ""
                
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(hwnd):
                print("微信窗口不可见")
                return ""
                
            # 检查窗口是否被最小化
            if win32gui.IsIconic(hwnd):
                print("微信窗口被最小化")
                return ""
                
            # 先保存剪贴板内容
            original = None
            try:
                win32clipboard.OpenClipboard()
                try:
                    original = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                except:
                    pass
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
            except:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
                    
            try:
                # 激活窗口
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)
                
                # 模拟Ctrl+A
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('A'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # 模拟Ctrl+C
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('C'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.3)
                
                # 获取文本
                text = ""
                try:
                    win32clipboard.OpenClipboard()
                    try:
                        text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    except:
                        pass
                    win32clipboard.EmptyClipboard()
                finally:
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
                        
                # 恢复原始剪贴板
                if original:
                    try:
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                        win32clipboard.CloseClipboard()
                    except:
                        try:
                            win32clipboard.CloseClipboard()
                        except:
                            pass
                            
                if text and text.strip():
                    print(f"获取到微信文本: {text}")
                    return text
                    
            except Exception as e:
                print(f"微信操作错误: {e}")
                
            return ""
            
        except Exception as e:
            print(f"微信获取文本错误: {e}")
            return ""

    def set_text(self, hwnd: int, text: str) -> bool:
        try:
            # 先保存剪贴板内容
            original = None
            win32clipboard.OpenClipboard()
            try:
                original = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            except:
                pass
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            
            # 设置新文本到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            
            # 模拟Ctrl+A
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 模拟Ctrl+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 恢复原始剪贴板
            if original:
                time.sleep(0.2)
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                
            return True
            
        except Exception as e:
            print(f"微信设置文本错误: {e}")
            if original:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(original, win32con.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                except:
                    pass
            return False

class ChromeHandler(WindowHandler):
    """Chrome/Vivaldi窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return "Chrome_WidgetWin_1" in class_name
        
    def get_text(self, hwnd: int) -> str:
        try:
            # 先尝试使用UI Automation
            import uiautomation as auto
            element = auto.ControlFromHandle(hwnd)
            if element:
                text = element.GetValuePattern().Value
                if text and text.strip():
                    print(f"通过UI Automation获取到文本: {text}")
                    return text
                    
            # 如果失败，尝试使用剪贴板方法
            print("UI Automation失败，尝试剪贴板方法")
            return self.get_text_by_clipboard(hwnd)
            
        except Exception as e:
            print(f"Chrome获取文本错误: {e}")
            return self.get_text_by_clipboard(hwnd)

    def set_text(self, hwnd: int, text: str) -> bool:
        try:
            # 先尝试使用UI Automation
            import uiautomation as auto
            element = auto.ControlFromHandle(hwnd)
            if element:
                try:
                    element.GetValuePattern().SetValue(text)
                    print("通过UI Automation设置文本成功")
                    return True
                except:
                    print("UI Automation设置失败")
                    
            # 如果失败，使用剪贴板方法
            print("尝试使用剪贴板方法")
            return self.set_text_by_clipboard(hwnd, text)
            
        except Exception as e:
            print(f"Chrome设置文本错误: {e}")
            return self.set_text_by_clipboard(hwnd, text)

class FirefoxHandler(WindowHandler):
    """Firefox窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return "MozillaWindowClass" in class_name
        
    def get_text(self, hwnd: int) -> str:
        # Firefox使用自定义消息
        try:
            # 获取实际的编辑框句柄
            edit_hwnd = win32gui.FindWindowEx(hwnd, 0, "MozillaEditableWindowClass", None)
            if not edit_hwnd:
                edit_hwnd = hwnd
                
            # 使用accessibility API获取文本
            import comtypes.client
            acc = comtypes.client.GetFocusedObject()
            if acc:
                return acc.accValue(0) or ""
        except:
            pass
        return super().get_text(hwnd)

class DefaultHandler(WindowHandler):
    """默认窗口处理器"""
    def can_handle(self, hwnd: int, class_name: str) -> bool:
        return True

class SimpleTranslator:
    def __init__(self):
        """初始化翻译器"""
        self.shift_pressed = False
        self.f11_pressed = False     # 使用 Shift+F11 翻译
        self.f12_pressed = False     # 使用 Shift+F12 退出
        self.last_translation_time = 0
        self.keyboard = Controller()
        print("✓ 翻译器初始化完成")
        print("等待快捷键触发:")
        print("- Shift+F11: 翻译")
        print("- Shift+F12: 退出程序")
        
        # 注册窗口处理器
        self.handlers = [
            NotepadHandler(),  # 记事本处理器放在最前面
            QQHandler(),
            DingTalkHandler(),
            WeChatHandler(),
            ChromeHandler(),
            FirefoxHandler(),
            DefaultHandler()
        ]

    def get_window_class(self, hwnd) -> str:
        """获取窗口类名"""
        try:
            return win32gui.GetClassName(hwnd)
        except:
            return ""

    def get_window_text(self, hwnd) -> str:
        """获取窗口文本"""
        try:
            class_name = self.get_window_class(hwnd)
            print(f"窗口类名: {class_name}")  # 调试信息
            
            # 查找合适的处理器
            for handler in self.handlers:
                if handler.can_handle(hwnd, class_name):
                    text = handler.get_text(hwnd)
                    if text:
                        return text
            
            # 如果所有处理器都失败，使用剪贴板方法
            return self.get_text_by_clipboard(hwnd)
            
        except Exception as e:
            print(f"获取文本错误: {e}")
            return ""

    def get_chrome_text(self, hwnd) -> str:
        """获取Chrome浏览器文本"""
        try:
            # 使用Chrome特定的消息
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            return buffer[:length].tobytes().decode('utf-16')
        except:
            return self.get_text_by_clipboard(hwnd)

    def get_firefox_text(self, hwnd) -> str:
        """获取Firefox浏览器文本"""
        try:
            # 使用Firefox特定的消息
            length = windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            buffer = win32gui.PyMakeBuffer(length + 1)
            windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            return buffer[:length].tobytes().decode('utf-16')
        except:
            return self.get_text_by_clipboard(hwnd)

    def get_edit_text(self, hwnd) -> str:
        """获取编辑框文本"""
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            return buffer[:length].tobytes().decode('utf-16')
        except:
            return self.get_text_by_clipboard(hwnd)

    def send_keys(self, keys):
        """发送按键序列"""
        for vk, up in keys:
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP if up else 0, 0)
            time.sleep(0.05)

    def set_window_text(self, hwnd, text: str) -> bool:
        """设置窗口文本"""
        try:
            # 清空剪贴板并设置新文本
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            # 激活目标窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            
            # 模拟Ctrl+A
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # 模拟Ctrl+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            return True
            
        except Exception as e:
            print(f"设置文本错误: {e}")
            return False

    def translate_text(self, text: str) -> Optional[str]:
        """使用Google Translate API翻译文本"""
        if not text or not text.strip():
            print("文本为空，跳过翻译")
            return None
            
        try:
            print(f"正在翻译: {text}")
            response = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={
                    "client": "gtx",
                    "sl": "zh-CN",  # 指定源语言为中文
                    "tl": "en",     # 目标语言为英文
                    "dt": "t",
                    "q": text.strip()  # 去除首尾空白
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and result[0]:
                    translated = ''.join([item[0] for item in result[0] if item[0]])
                    if translated and translated.strip():
                        print(f"翻译结果: {translated}")
                        return translated
                    else:
                        print("翻译结果为空")
                else:
                    print("翻译结果格式错误")
            else:
                print(f"翻译请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
            return None
            
        except Exception as e:
            print(f"翻译错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def handle_translation(self):
        """处理翻译"""
        try:
            # 获取当前窗口
            hwnd = win32gui.GetForegroundWindow()
            
            # 检查窗口是否有效
            if not hwnd or hwnd == 0:
                print("无效的窗口句柄")
                return
                
            # 获取窗口类名和标题
            class_name = self.get_window_class(hwnd)
            window_title = win32gui.GetWindowText(hwnd)
            
            # 扩展系统窗口检查
            system_classes = [
                "Windows.UI.Core",
                "Shell_",
                "NotifyIconOverflowWindow",
                "Windows.UI.Notification",
                "Windows.UI.Core.CoreWindow",
                "ApplicationFrameWindow",
                "Windows.UI.Popups",
                "TaskManagerWindow",
                "ForegroundStaging",
                "SystemTray_Main"
            ]
            
            if any(cls in class_name for cls in system_classes):
                print(f"跳过系统窗口: {class_name}")
                return
                
            # 检查窗口标题是否包含系统相关字符
            system_titles = [
                "通知中心",
                "操作中心",
                "任务管理器",
                "系统托盘",
                "Action Center",
                "Notification",
                "Task Manager"
            ]
            
            if any(title in window_title for title in system_titles):
                print(f"跳过系统窗口: {window_title}")
                return
                
            # 检查窗口状态
            if not win32gui.IsWindowVisible(hwnd):
                print("窗口不可见")
                return
                
            if win32gui.IsIconic(hwnd):
                print("窗口被最小化")
                return
                
            # 检查窗口是否是对话框或弹出窗口
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            if (style & win32con.WS_POPUP) or (ex_style & win32con.WS_EX_TOOLWINDOW):
                print("跳过弹出窗口或工具窗口")
                return
                
            print(f"\n当前窗口: {window_title}")
            print(f"窗口类名: {class_name}")

            # 获取文本
            text = None
            for handler in self.handlers:
                if handler.can_handle(hwnd, class_name):
                    text = handler.get_text(hwnd)
                    if text and text.strip():
                        break
                        
            if not text:
                print("未获取到文本")
                return

            print(f"原文: {text}")
            
            # 检查是否是英文
            if all(ord(c) < 128 for c in text.strip()):
                print("检测到英文文本，跳过翻译")
                return
            
            # 翻译前再次检查窗口状态
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                print("窗口状态已改变")
                return
                
            # 翻译
            translated = self.translate_text(text)
            if not translated:
                print("翻译失败，保留原文")
                return

            print(f"译文: {translated}")
            
            # 比较原文和译文（忽略空白字符）
            if translated.strip() == text.strip():
                print("翻译结果与原文相同，不做替换")
                return
                
            # 最后一次检查窗口状态
            if not win32gui.IsWindow(hwnd):
                print("窗口已失效")
                return
                
            current_hwnd = win32gui.GetForegroundWindow()
            if current_hwnd != hwnd:
                print("窗口已改变")
                return
                
            # 替换文本
            success = False
            for handler in self.handlers:
                if handler.can_handle(hwnd, class_name):
                    if handler.set_text(hwnd, translated):
                        print("✓ 文本替换成功")
                        success = True
                        break
                        
            if not success:
                print("✗ 文本替换失败")

        except Exception as e:
            print(f"翻译处理错误: {e}")
            import traceback
            traceback.print_exc()

    def on_press(self, key):
        """按键按下事件"""
        try:
            if key == keyboard.Key.shift:
                self.shift_pressed = True
            elif key == keyboard.Key.f11:
                self.f11_pressed = True
            elif key == keyboard.Key.f12:
                self.f12_pressed = True

            # 检查组合键
            if self.shift_pressed and self.f11_pressed:
                print("检测到翻译快捷键，开始翻译...")
                self.handle_translation()
            elif self.shift_pressed and self.f12_pressed:
                print("检测到退出快捷键，程序即将退出...")
                import sys
                sys.exit(0)

        except AttributeError:
            pass

    def on_release(self, key):
        """按键释放事件"""
        try:
            if key == keyboard.Key.shift:
                self.shift_pressed = False
            elif key == keyboard.Key.f11:
                self.f11_pressed = False
            elif key == keyboard.Key.f12:
                self.f12_pressed = False
        except AttributeError:
            pass

    def run(self):
        """运行翻译器"""
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()

def main():
    translator = SimpleTranslator()
    translator.run()

if __name__ == "__main__":
    main() 