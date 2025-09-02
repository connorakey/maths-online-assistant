use reqwest;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OpenAiRequestType {
    StepByStep,
    FinalAnswer,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenAiRequest {
    pub image_b64: String,
    pub api_key: String,
    pub request_type: OpenAiRequestType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenAiRequestWithUrl {
    pub image_b64: String,
    pub api_key: String,
    pub request_type: OpenAiRequestType,
    pub base_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenAiResponse {
    pub success: bool,
    pub response: String,
}

#[tauri::command]
pub async fn send_openai_request(request: OpenAiRequest, base_url: String) -> Result<OpenAiResponse, String> {
    if request.image_b64.is_empty() {
        return Err("Image data is empty".to_string());
    }

    if request.api_key.is_empty() {
        return Err("API key is empty".to_string());
    }

    if base_url.is_empty() {
        return Err("Base URL is empty".to_string());
    }

    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(60))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

    let api_url = format!("{}/api/openai", base_url.trim_end_matches('/'));

    let json_body = serde_json::to_string(&request)
        .map_err(|e| format!("Failed to serialize request: {}", e))?;

    let response = client
        .post(&api_url)
        .header("Content-Type", "application/json")
        .header("User-Agent", "Maths-Online-Tutor/1.0")
        .body(json_body)
        .send()
        .await
        .map_err(|e| {
            if e.is_timeout() {
                "Request timed out after 60 seconds".to_string()
            } else if e.is_connect() {
                "Failed to connect to the server".to_string()
            } else {
                format!("Failed to send request: {}", e)
            }
        })?;

    let status = response.status();
    
    let response_text = response.text().await
        .map_err(|e| format!("Failed to read response: {}", e))?;

    match status {
        reqwest::StatusCode::OK => {
            let api_response = serde_json::from_str::<OpenAiResponse>(&response_text)
                .map_err(|e| format!("Failed to parse response: {}", e))?;
            Ok(api_response)
        }
        reqwest::StatusCode::UNAUTHORIZED => {
            let api_response = serde_json::from_str::<OpenAiResponse>(&response_text)
                .map_err(|_| "Invalid API key".to_string())?;
            Ok(api_response)
        }
        reqwest::StatusCode::BAD_REQUEST => {
            let api_response = serde_json::from_str::<OpenAiResponse>(&response_text)
                .map_err(|e| format!("Failed to parse error response: {}", e))?;
            Ok(api_response)
        }
        reqwest::StatusCode::INTERNAL_SERVER_ERROR => {
            let api_response = serde_json::from_str::<OpenAiResponse>(&response_text)
                .map_err(|_| "Internal server error".to_string())?;
            Ok(api_response)
        }
        status => {
            Err(format!("HTTP {}: {}", status, response_text))
        }
    }
}

#[tauri::command]
pub async fn test_api_connection(base_url: String) -> Result<bool, String> {
    if base_url.is_empty() {
        return Err("Base URL is empty".to_string());
    }

    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

    let api_url = format!("{}/api/openai", base_url.trim_end_matches('/'));

    let test_request = serde_json::json!({
        "image_b64": "test",
        "api_key": "test",
        "request_type": "StepByStep"
    });

    let json_body = serde_json::to_string(&test_request)
        .map_err(|e| format!("Failed to serialize test request: {}", e))?;

    let response = client
        .post(&api_url)
        .header("Content-Type", "application/json")
        .header("User-Agent", "Maths-Online-Tutor/1.0")
        .body(json_body)
        .send()
        .await;

    match response {
        Ok(resp) => {
            Ok(resp.status().is_client_error() || resp.status().is_success())
        }
        Err(_) => Ok(false),
    }
}

pub fn validate_base64_image(base64_data: &str) -> Result<(), String> {
    if base64_data.is_empty() {
        return Err("Base64 data is empty".to_string());
    }

    let clean_data = if base64_data.starts_with("data:image/") {
        if let Some(comma_index) = base64_data.find(',') {
            &base64_data[comma_index + 1..]
        } else {
            return Err("Invalid data URL format".to_string());
        }
    } else {
        base64_data
    };

    match BASE64.decode(clean_data) {
        Ok(_) => Ok(()),
        Err(_) => Err("Invalid base64 data".to_string()),
    }
}

pub fn get_request_type_string(request_type: &OpenAiRequestType) -> &'static str {
    match request_type {
        OpenAiRequestType::StepByStep => "StepByStep",
        OpenAiRequestType::FinalAnswer => "FinalAnswer",
    }
}