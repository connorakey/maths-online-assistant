use axum::{routing::post, Json, Router, http::StatusCode, extract::DefaultBodyLimit};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use backend::openai::{get_step_by_step_guidance, get_final_answer};
use backend::database::{is_valid_api_key, is_root_api_key, add_api_key as db_add_api_key, init_db, test_connection};
use backend::ratelimit::check_rate_limit;

// An enum to determine the type of request
#[derive(Debug, Deserialize)]
pub enum OpenAiRequestType {
    StepByStep,
    FinalAnswer,
}

// A struct to hold the request data
#[derive(Debug, Deserialize)]
pub struct OpenAiRequest {
    image_b64: String,
    api_key: String,
    request_type: OpenAiRequestType,
}

// A struct to hold the response data
#[derive(Debug, Serialize)]
pub struct OpenAiResponse {
    success: bool,
    response: String,
}

// A struct to hold the add API key request data
#[derive(Debug, Deserialize)]
pub struct AddApiKeyRequest {
    api_key: String,
    new_api_key: String,
    is_root: bool,
}

// A struct to hold the add API key response data
#[derive(Debug, Serialize)]
pub struct AddApiKeyResponse {
    success: bool,
    response: String,
}

#[tokio::main]
async fn main() {
    dotenv::dotenv().ok();

    test_connection().await.unwrap();
    init_db().await.unwrap();

    let app = Router::new()
        .route("/api/openai", post(openai))
        .route("/admin/add_api_key", post(add_api_key))
        .layer(DefaultBodyLimit::max(100 * 1024 * 1024)); // 100MB limit

    // Get port from environment variable, default to 3000 if not set
    let port = std::env::var("PORT").unwrap_or_else(|_| "3000".to_string());
    let addr: SocketAddr = format!("127.0.0.1:{}", port).parse().unwrap();
    println!("listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app)
        .await
        .unwrap();
}

async fn openai(Json(payload): Json<OpenAiRequest>) -> (StatusCode, Json<OpenAiResponse>) {
    match is_valid_api_key(&payload.api_key).await {
        Ok(is_valid) => {
            if !is_valid {
                return (StatusCode::UNAUTHORIZED, Json(OpenAiResponse {
                    success: false,
                    response: "Invalid API key".to_string(),
                }));
            }
            if !check_rate_limit(&payload.api_key) {
                return (StatusCode::TOO_MANY_REQUESTS, Json(OpenAiResponse {
                    success: false,
                    response: "Rate limit exceeded".to_string(),
                }));
            }
        }
        Err(e) => {
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(OpenAiResponse {
                success: false,
                response: format!("Database error while validating API key: {}", e),
            }));
        }
    }

    let result = match payload.request_type {
        OpenAiRequestType::StepByStep => get_step_by_step_guidance(&payload.image_b64).await,
        OpenAiRequestType::FinalAnswer => get_final_answer(&payload.image_b64).await,
    };

    match result {
        Ok(response_text) => {
            (StatusCode::OK, Json(OpenAiResponse {
                success: true,
                response: response_text,
            }))
        }
        Err(e) => {
            (StatusCode::BAD_REQUEST, Json(OpenAiResponse {
                success: false,
                response: format!("An error occurred: {}", e),
            }))
        }
    }
}

pub async fn add_api_key(Json(payload): Json<AddApiKeyRequest>) -> (StatusCode, Json<AddApiKeyResponse>) {
    match is_root_api_key(&payload.api_key).await {
        Ok(is_root) => {
            if !is_root {
                return (StatusCode::FORBIDDEN, Json(AddApiKeyResponse {
                    success: false,
                    response: "Access denied: Root privileges required".to_string(),
                }));
            }
        }
        Err(e) => {
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(AddApiKeyResponse {
                success: false,
                response: format!("Database error while validating API key: {}", e),
            }));
        }
    }

    match db_add_api_key(&payload.new_api_key, payload.is_root).await {
        Ok(message) => {
            (StatusCode::OK, Json(AddApiKeyResponse {
                success: true,
                response: message,
            }))
        }
        Err(e) => {
            (StatusCode::BAD_REQUEST, Json(AddApiKeyResponse {
                success: false,
                response: format!("Failed to add API key: {}", e),
            }))
        }
    }
}