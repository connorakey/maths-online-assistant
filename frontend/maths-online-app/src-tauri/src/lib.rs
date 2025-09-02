mod screenshot;
mod request;
mod settings;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
      screenshot::capture_screenshot,
      request::send_openai_request,
      request::test_api_connection,
      settings::get_settings,
      settings::verify_settings_password,
      settings::save_settings,
      settings::change_settings_password,
      settings::get_screenshot_coordinates,
    ])
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}