#[cfg(target_os = "windows")]
pub fn simulate_paste(_text: &str) {
    use windows::Win32::UI::Input::KeyboardAndMouse::*;
    use std::{thread, time::Duration};

    unsafe {
        // 粘贴操作 (Ctrl+V)
        keybd_event(VK_CONTROL.0 as u8, 0, KEYBD_EVENT_FLAGS(0), 0);
        keybd_event(b'V', 0, KEYBD_EVENT_FLAGS(0), 0);
        thread::sleep(Duration::from_millis(50));
        keybd_event(b'V', 0, KEYBD_EVENT_FLAGS(2), 0);
        keybd_event(VK_CONTROL.0 as u8, 0, KEYBD_EVENT_FLAGS(2), 0);
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