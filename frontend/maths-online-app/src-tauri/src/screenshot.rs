use screenshots::Screen;
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use image::{DynamicImage, GenericImageView, ImageFormat};
use std::io::{BufWriter, Cursor};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreenshotArea {
    pub x1: u32,
    pub x2: u32,
    pub y1: u32,
    pub y2: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreenshotResponse {
    pub success: bool,
    pub base64_data: String,
    pub error: Option<String>,
}

#[tauri::command]
pub fn capture_screenshot(area: ScreenshotArea) -> ScreenshotResponse {
    match capture_and_optimize_screenshot(area) {
        Ok(base64_data) => ScreenshotResponse {
            success: true,
            base64_data,
            error: None,
        },
        Err(e) => ScreenshotResponse {
            success: false,
            base64_data: String::new(),
            error: Some(e),
        },
    }
}

fn capture_and_optimize_screenshot(area: ScreenshotArea) -> Result<String, String> {
    let screens = Screen::all()
        .map_err(|e| format!("Failed to get screens: {}", e))?;
    
    let screen = screens.first()
        .ok_or("No screens found")?;
    
    // Convert u32 to i32 for x, y coordinates and calculate width/height
    let x = area.x1 as i32;
    let y = area.y1 as i32;
    let width = area.x2 - area.x1;
    let height = area.y2 - area.y1;
    
    let screenshot = screen.capture_area(x, y, width, height)
        .map_err(|e| format!("Failed to capture screenshot: {}", e))?;

    // Convert RgbaImage to DynamicImage
    let dynamic_image = DynamicImage::ImageRgba8(screenshot);
    let base64_data = optimize_and_encode(dynamic_image)?;
    
    Ok(base64_data)
}

#[tauri::command]
pub fn optimize_and_encode(img: DynamicImage) -> Result<String, String> {
    let optimized = optimize_image(img);
    image_to_base64_optimized(optimized)
}

pub fn optimize_image(img: DynamicImage) -> DynamicImage {
    let (width, height) = img.dimensions();
    
    let max_width = 2560;
    let max_height = 1440;
    
    if width > max_width || height > max_height {
        let ratio = (max_width as f32 / width as f32).min(max_height as f32 / height as f32);
        let new_width = (width as f32 * ratio) as u32;
        let new_height = (height as f32 * ratio) as u32;
        
        img.resize(new_width, new_height, image::imageops::FilterType::Lanczos3)
    } else {
        img
    }
}

pub fn image_to_base64_optimized(img: DynamicImage) -> Result<String, String> {
    let mut buf = Vec::new();
    let mut writer = BufWriter::new(Cursor::new(&mut buf));
    
    img.write_to(&mut writer, ImageFormat::Jpeg)
       .map_err(|e| format!("Failed to encode image: {}", e))?;
    
    drop(writer);
    
    Ok(BASE64.encode(&buf))
}