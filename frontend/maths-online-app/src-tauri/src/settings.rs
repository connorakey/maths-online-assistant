use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreenshotCoordinates {
    pub x1: u32,
    pub y1: u32,
    pub x2: u32,
    pub y2: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SettingsData {
    pub api_key: String,
    pub screenshot_coords: ScreenshotCoordinates,
    pub base_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PasswordHashes {
    pub api_key: String,
    pub screenshot_coords: String,
}

impl Default for SettingsData {
    fn default() -> Self {
        Self {
            api_key: String::new(),
            screenshot_coords: ScreenshotCoordinates {
                x1: 0,
                y1: 0,
                x2: 100,
                y2: 100,
            },
            base_url: "http://localhost:8080".to_string(),
        }
    }
}

impl Default for PasswordHashes {
    fn default() -> Self {
        Self {
            // Default password hashes (password: "admin123")
            api_key: "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9".to_string(),
            screenshot_coords: "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9".to_string(),
        }
    }
}

fn get_settings_dir(app_handle: &AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data directory: {}", e))?;
    
    Ok(app_data_dir)
}

fn get_settings_path(app_handle: &AppHandle) -> Result<PathBuf, String> {
    let settings_dir = get_settings_dir(app_handle)?;
    Ok(settings_dir.join("settings.json"))
}

fn get_passwords_path(app_handle: &AppHandle) -> Result<PathBuf, String> {
    let settings_dir = get_settings_dir(app_handle)?;
    Ok(settings_dir.join("passwords.json"))
}

fn ensure_settings_dir(app_handle: &AppHandle) -> Result<(), String> {
    let settings_dir = get_settings_dir(app_handle)?;
    if !settings_dir.exists() {
        fs::create_dir_all(&settings_dir)
            .map_err(|e| format!("Failed to create settings directory: {}", e))?;
    }
    Ok(())
}

fn hash_password(password: &str) -> String {
    use sha2::{Sha256, Digest};
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    format!("{:x}", hasher.finalize())
}

#[tauri::command]
pub fn get_settings(app_handle: AppHandle) -> Result<SettingsData, String> {
    ensure_settings_dir(&app_handle)?;
    
    let settings_path = get_settings_path(&app_handle)?;
    
    if !settings_path.exists() {
        let default_settings = SettingsData::default();
        save_settings_file(&app_handle, &default_settings)?;
        return Ok(default_settings);
    }
    
    let content = fs::read_to_string(&settings_path)
        .map_err(|e| format!("Failed to read settings file: {}", e))?;
    
    let settings: SettingsData = serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse settings: {}", e))?;
    
    Ok(settings)
}

fn save_settings_file(app_handle: &AppHandle, settings: &SettingsData) -> Result<(), String> {
    ensure_settings_dir(app_handle)?;
    
    let settings_path = get_settings_path(app_handle)?;
    let content = serde_json::to_string_pretty(settings)
        .map_err(|e| format!("Failed to serialize settings: {}", e))?;
    
    fs::write(&settings_path, content)
        .map_err(|e| format!("Failed to write settings file: {}", e))?;
    
    Ok(())
}

fn get_password_hashes(app_handle: &AppHandle) -> Result<PasswordHashes, String> {
    ensure_settings_dir(app_handle)?;
    
    let passwords_path = get_passwords_path(app_handle)?;
    
    if !passwords_path.exists() {
        let default_passwords = PasswordHashes::default();
        save_password_hashes(app_handle, &default_passwords)?;
        return Ok(default_passwords);
    }
    
    let content = fs::read_to_string(&passwords_path)
        .map_err(|e| format!("Failed to read passwords file: {}", e))?;
    
    let passwords: PasswordHashes = serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse passwords: {}", e))?;
    
    Ok(passwords)
}

fn save_password_hashes(app_handle: &AppHandle, passwords: &PasswordHashes) -> Result<(), String> {
    ensure_settings_dir(app_handle)?;
    
    let passwords_path = get_passwords_path(app_handle)?;
    let content = serde_json::to_string_pretty(passwords)
        .map_err(|e| format!("Failed to serialize passwords: {}", e))?;
    
    fs::write(&passwords_path, content)
        .map_err(|e| format!("Failed to write passwords file: {}", e))?;
    
    Ok(())
}

#[tauri::command]
pub fn verify_settings_password(
    app_handle: AppHandle,
    section: String,
    password: String,
) -> Result<bool, String> {
    let password_hashes = get_password_hashes(&app_handle)?;
    let hashed_input = hash_password(&password);
    
    let expected_hash = match section.as_str() {
        "apiKey" => &password_hashes.api_key,
        "screenshotCoords" => &password_hashes.screenshot_coords,
        _ => return Err("Invalid section".to_string()),
    };
    
    Ok(hashed_input == *expected_hash)
}

#[tauri::command]
pub fn save_settings(
    app_handle: AppHandle,
    settings: SettingsData,
    unlocked_sections: Vec<String>,
) -> Result<(), String> {
    let mut current_settings = get_settings(app_handle.clone())?;
    
    // Only update unlocked sections
    for section in unlocked_sections {
        match section.as_str() {
            "apiKey" => {
                current_settings.api_key = settings.api_key.clone();
            }
            "screenshotCoords" => {
                current_settings.screenshot_coords = settings.screenshot_coords.clone();
            }
            _ => {
                return Err(format!("Invalid section: {}", section));
            }
        }
    }
    
    // Always allow base_url to be updated (no password protection)
    current_settings.base_url = settings.base_url;
    
    save_settings_file(&app_handle, &current_settings)?;
    Ok(())
}

#[tauri::command]
pub fn change_settings_password(
    app_handle: AppHandle,
    section: String,
    old_password: String,
    new_password: String,
) -> Result<(), String> {
    // Verify old password first
    if !verify_settings_password(app_handle.clone(), section.clone(), old_password)? {
        return Err("Invalid current password".to_string());
    }
    
    let mut password_hashes = get_password_hashes(&app_handle)?;
    let new_hash = hash_password(&new_password);
    
    match section.as_str() {
        "apiKey" => {
            password_hashes.api_key = new_hash;
        }
        "screenshotCoords" => {
            password_hashes.screenshot_coords = new_hash;
        }
        _ => return Err("Invalid section".to_string()),
    }
    
    save_password_hashes(&app_handle, &password_hashes)?;
    Ok(())
}

#[tauri::command]
pub fn get_screenshot_coordinates(app_handle: AppHandle) -> Result<ScreenshotCoordinates, String> {
    let settings = get_settings(app_handle)?;
    Ok(settings.screenshot_coords)
}
