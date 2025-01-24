// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backup;
mod clipboard;
mod cmd;
mod config;
mod error;
mod hotkey;
mod lang_detect;
mod screenshot;
mod server;
mod system_ocr;
mod tray;
mod updater;
mod window;
mod keyboard;

use backup::*;
use clipboard::*;
use cmd::*;
use config::*;
use hotkey::*;
use lang_detect::*;
use log::{info, warn};
use once_cell::sync::OnceCell;
use screenshot::screenshot;
use server::*;
use std::sync::Mutex;
use system_ocr::*;
use tauri::api::notification::Notification;
use tauri::Manager;
use tauri::AppHandle;
use tauri_plugin_log::LogTarget;
use tray::*;
use updater::check_update;
use window::config_window;
use window::updater_window;
use tauri::GlobalShortcutManager;
use window::{translate_and_replace, translate_window};

// Global AppHandle
pub static APP: OnceCell<tauri::AppHandle> = OnceCell::new();

// Text to be translated
pub struct StringWrapper(pub Mutex<String>);

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _, cwd| {
            Notification::new(&app.config().tauri.bundle.identifier)
                .title("The program is already running. Please do not start it again!")
                .body(cwd)
                .icon("pot")
                .show()
                .unwrap();
        }))
        .plugin(
            tauri_plugin_log::Builder::default()
                .targets([LogTarget::LogDir, LogTarget::Stdout])
                .build(),
        )
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            Some(vec![]),
        ))
        .plugin(tauri_plugin_sql::Builder::default().build())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_fs_watch::init())
        .system_tray(tauri::SystemTray::new())
        .setup(|app| {
            info!("============== Start App ==============");
            #[cfg(target_os = "macos")]
            {
                app.set_activation_policy(tauri::ActivationPolicy::Accessory);
                let trusted =
                    macos_accessibility_client::accessibility::application_is_trusted_with_prompt();
                info!("MacOS Accessibility Trusted: {}", trusted);
            }
            // Global AppHandle
            APP.get_or_init(|| app.handle());
            // Init Config
            info!("Init Config Store");
            init_config(app);
            // Check First Run
            if is_first_run() {
                // Open Config Window
                info!("First Run, opening config window");
                config_window();
            }
            app.manage(StringWrapper(Mutex::new("".to_string())));
            // Update Tray Menu
            update_tray(app.app_handle(), "".to_string(), "".to_string());
            // Start http server
            start_server();
            // Register Global Shortcut
            info!("Registering shortcut: CommandOrControl+Alt+T");
            let app_handle = app.handle();
            let handle = app_handle.clone();
            if let Err(e) = app.global_shortcut_manager().register("CommandOrControl+Alt+T", move || {
                let handle = handle.clone();
                tauri::async_runtime::spawn(async move {
                    translate_and_replace().await;
                });
            }) {
                warn!("Failed to register shortcut: {}", e);
            }
            match get("proxy_enable") {
                Some(v) => {
                    if v.as_bool().unwrap() && get("proxy_host").map_or(false, |host| !host.as_str().unwrap().is_empty()) {
                        let _ = set_proxy();
                    }
                }
                None => {}
            }
            // Check Update
            check_update(app.handle());
            if let Some(engine) = get("translate_detect_engine") {
                if engine.as_str().unwrap() == "local" {
                    init_lang_detect();
                }
            }
            let clipboard_monitor = match get("clipboard_monitor") {
                Some(v) => v.as_bool().unwrap(),
                None => {
                    set("clipboard_monitor", false);
                    false
                }
            };
            app.manage(ClipboardMonitorEnableWrapper(Mutex::new(
                clipboard_monitor.to_string(),
            )));
            start_clipboard_monitor(app.handle());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            reload_store,
            get_text,
            cut_image,
            get_base64,
            copy_img,
            system_ocr,
            set_proxy,
            unset_proxy,
            run_binary,
            open_devtools,
            register_shortcut_by_frontend,
            update_tray,
            updater_window,
            screenshot,
            lang_detect,
            webdav,
            local,
            install_plugin,
            font_list,
            aliyun,
            register_translate_shortcut
        ])
        .on_system_tray_event(tray_event_handler)
        .build(tauri::generate_context!())
        .expect("error while running tauri application")
        // 窗口关闭不退出
        .run(|_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { api, .. } = event {
                api.prevent_exit();
            }
        });
}

#[tauri::command]
async fn register_translate_shortcut(app: AppHandle, shortcut: String) -> Result<(), String> {
    let _ = app.global_shortcut_manager().unregister_all();
    
    app.global_shortcut_manager()
        .register(&shortcut, move || {
            tauri::async_runtime::spawn(async move {
                translate_and_replace().await;
            });
        })
        .map_err(|e| e.to_string())
}

// 获取选中文本的函数
fn get_selected_text() -> Result<String, Box<dyn std::error::Error>> {
    #[cfg(target_os = "windows")]
    {
        use clipboard::get_selected_text as win_get_selected_text;
        win_get_selected_text()
    }
    #[cfg(target_os = "macos")]
    {
        use clipboard::get_selected_text as mac_get_selected_text;
        mac_get_selected_text()
    }
    #[cfg(target_os = "linux")]
    {
        use clipboard::get_selected_text as linux_get_selected_text;
        linux_get_selected_text()
    }
}
