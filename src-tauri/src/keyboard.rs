#[cfg(target_os = "windows")]
pub fn simulate_paste(text: &str) {
    use windows::Win32::UI::Input::KeyboardAndMouse::*;
    use windows::Win32::UI::WindowsAndMessaging::*;
    use std::{thread, time::Duration};

    unsafe {
        // 先全选当前文本 (Ctrl+A)
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'A', 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'A', 0, KEYEVENTF_KEYUP, 0);
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYUP, 0);

        // 短暂延迟
        thread::sleep(Duration::from_millis(50));

        // 复制当前文本 (Ctrl+C)
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'C', 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'C', 0, KEYEVENTF_KEYUP, 0);
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYUP, 0);

        // 等待复制完成
        thread::sleep(Duration::from_millis(100));

        // 粘贴翻译后的文本 (Ctrl+V)
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'V', 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(b'V', 0, KEYEVENTF_KEYUP, 0);
        keybd_event(VK_CONTROL.0 as u8, 0, KEYEVENTF_KEYUP, 0);
    }
}

#[cfg(target_os = "linux")]
pub fn simulate_paste(text: &str) {
    // Linux 实现
}

#[cfg(target_os = "macos")]
pub fn simulate_paste(text: &str) {
    // macOS 实现
} 