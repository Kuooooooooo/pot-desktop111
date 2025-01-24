use crate::window::text_translate;
use std::sync::Mutex;
use tauri::{ClipboardManager, Manager};

pub struct ClipboardMonitorEnableWrapper(pub Mutex<String>);

pub fn start_clipboard_monitor(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let mut pre_text = "".to_string();
        loop {
            let handle = app_handle.app_handle();
            let state = handle.state::<ClipboardMonitorEnableWrapper>();
            if let Ok(clipboard_monitor) = state.0.try_lock() {
                if clipboard_monitor.contains("true") {
                    if let Ok(result) = app_handle.clipboard_manager().read_text() {
                        match result {
                            Some(v) => {
                                if v != pre_text {
                                    text_translate(v.clone());
                                    pre_text = v;
                                }
                            }
                            None => {}
                        }
                    }
                } else {
                    break;
                }
            }
            std::thread::sleep(std::time::Duration::from_millis(500));
        }
    });
}

#[cfg(target_os = "windows")]
pub fn get_selected_text() -> Result<String, Box<dyn std::error::Error>> {
    use arboard::Clipboard;
    let mut clipboard = Clipboard::new()?;
    clipboard.get_text().map_err(|e| e.into())
}

#[cfg(target_os = "macos")]
pub fn get_selected_text() -> Result<String, Box<dyn std::error::Error>> {
    // macOS 实现
    use arboard::Clipboard;
    let mut clipboard = Clipboard::new()?;
    Ok(clipboard.get_text()?)
}

#[cfg(target_os = "linux")]
pub fn get_selected_text() -> Result<String, Box<dyn std::error::Error>> {
    // Linux 实现
    use arboard::Clipboard;
    let mut clipboard = Clipboard::new()?;
    Ok(clipboard.get_text()?)
}
