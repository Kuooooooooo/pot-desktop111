use tauri::AppHandle;

pub async fn check_update(_app_handle: AppHandle) {
    // 由于禁用了 updater 特性，这里不执行任何更新检查
    // 仅保留函数签名以保证其他代码的兼容性
    #[cfg(debug_assertions)]
    println!("Update checking is disabled");
} 