use sqlx::{PgPool, Error as SqlxError, Row};
use std::env;
use dotenv;

/// Construct database URL from individual environment variables
fn get_database_url() -> Result<String, SqlxError> {
    let host = env::var("DB_HOST")
        .map_err(|_| SqlxError::Configuration("DB_HOST environment variable not set".into()))?;
    
    let port = env::var("DB_PORT")
        .map_err(|_| SqlxError::Configuration("DB_PORT environment variable not set".into()))?;
    
    let name = env::var("DB_NAME")
        .map_err(|_| SqlxError::Configuration("DB_NAME environment variable not set".into()))?;
    
    let user = env::var("DB_USER")
        .map_err(|_| SqlxError::Configuration("DB_USER environment variable not set".into()))?;
    
    let password = env::var("DB_PASSWORD")
        .map_err(|_| SqlxError::Configuration("DB_PASSWORD environment variable not set".into()))?;
    
    let database_url = format!("postgresql://{}:{}@{}:{}/{}", user, password, host, port, name);
    Ok(database_url)
}

/// Test the database connection by executing a simple query
pub async fn test_connection() -> Result<String, SqlxError> {
    dotenv::dotenv().ok();
    
    let database_url = get_database_url()?;
    
    let pool = PgPool::connect(&database_url).await?;
    
    let result = sqlx::query("SELECT 1 as test_value")
        .fetch_one(&pool)
        .await?;
    
    let test_value: i32 = result.get("test_value");
    
    pool.close().await;
    
    Ok(format!("Database connection successful! Test query returned: {}", test_value))
}

/// Create a database connection pool
pub async fn create_pool() -> Result<PgPool, SqlxError> {
    dotenv::dotenv().ok();
    
    let database_url = get_database_url()?;
    
    PgPool::connect(&database_url).await
}

/// Initialize database with all required tables
pub async fn init_db() -> Result<String, SqlxError> {
    let database_url = get_database_url()?;
    
    let pool = PgPool::connect(&database_url).await?;
    
    // Create the api_keys table
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            api_key VARCHAR(255) NOT NULL UNIQUE,
            root_api_key BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        "#
    )
    .execute(&pool)
    .await?;
    
    pool.close().await;
    
    Ok("Database initialized successfully!".to_string())
}


/// Checks if the api key is valid
pub async fn is_valid_api_key(api_key: &str) -> Result<bool, SqlxError> {
    let database_url = get_database_url()?;
    
    let pool = PgPool::connect(&database_url).await?;

    let result = sqlx::query(
        r#"
        SELECT COUNT(*) as count FROM api_keys WHERE api_key = $1
        "#
    )
    .bind(api_key)
    .fetch_one(&pool)
    .await?;
    
    let count: i64 = result.get("count");
    
    pool.close().await;
    
    Ok(count > 0)
}

/// Checks if the api key is a root key
pub async fn is_root_api_key(api_key: &str) -> Result<bool, SqlxError> {
    let database_url = get_database_url()?;
    
    let pool = PgPool::connect(&database_url).await?;

    let result = sqlx::query(
        r#"
        SELECT root_api_key FROM api_keys WHERE api_key = $1
        "#
    )
    .bind(api_key)
    .fetch_optional(&pool)
    .await?;
    
    pool.close().await;
    
    match result {
        Some(row) => {
            let is_root: bool = row.get("root_api_key");
            Ok(is_root)
        },
        None => Ok(false)
    }
}

/// Add a new API key to the database
pub async fn add_api_key(new_api_key: &str, is_root: bool) -> Result<String, SqlxError> {
    let database_url = get_database_url()?;
    
    let pool = PgPool::connect(&database_url).await?;

    // Check if API key already exists
    let existing = sqlx::query(
        r#"
        SELECT COUNT(*) as count FROM api_keys WHERE api_key = $1
        "#
    )
    .bind(new_api_key)
    .fetch_one(&pool)
    .await?;
    
    let count: i64 = existing.get("count");
    if count > 0 {
        pool.close().await;
        return Err(SqlxError::RowNotFound);
    }

    // Insert the new API key
    sqlx::query(
        r#"
        INSERT INTO api_keys (api_key, root_api_key) VALUES ($1, $2)
        "#
    )
    .bind(new_api_key)
    .bind(is_root)
    .execute(&pool)
    .await?;
    
    pool.close().await;
    
    Ok(format!("API key added successfully! Root privileges: {}", is_root))
}