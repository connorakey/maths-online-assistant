use async_openai::{
    types::{
        ChatCompletionRequestMessage, CreateChatCompletionRequestArgs,
        ChatCompletionRequestUserMessageContent, ImageUrl,
        ChatCompletionRequestSystemMessage, ChatCompletionRequestUserMessage,
        ChatCompletionRequestMessageContentPartImage,
        ChatCompletionRequestSystemMessageContent,
    },
    Client, config::OpenAIConfig,
};
use std::env;

/// Get step-by-step guidance for math questions without providing the final answer
pub async fn get_step_by_step_guidance(image_b64: &str) -> Result<String, Box<dyn std::error::Error>> {
    let api_key = env::var("OPENAI_API_KEY")
        .map_err(|_| "OpenAI API key is not set.")?;

    let config = OpenAIConfig::new().with_api_key(api_key);
    let client = Client::with_config(config);

    let system_message = ChatCompletionRequestSystemMessage {
        content: ChatCompletionRequestSystemMessageContent::Text(
            "You are a helpful assistant that guides Year 7 to 10 high school students, you will help them answer their math questions you will only provide step-by-step guidance using clear and simple explanations suitable for their level. You WILL NOT PROVIDE THE FINAL ANSWER! AND YOU MUST PROVIDE YOUR RESPONSE ONLY IN PLAIN MARKDOWN FORMAT. Math symbols should be in PLAIN text! Example: 2 to the power of 5 means 2 multiplied by itself 5 times, so you would figure this out by multiplying 2 by itself 5 time 2*2*2*2*2.".to_string()
        ),
        name: None,
    };

    // Handle both raw base64 and data URLs
    let image_url = if image_b64.starts_with("data:") {
        image_b64.to_string()
    } else {
        format!("data:image/jpeg;base64,{}", image_b64)
    };

    let image_content = ChatCompletionRequestMessageContentPartImage {
        image_url: ImageUrl {
            url: image_url,
            detail: None,
        },
    };

    let user_message = ChatCompletionRequestUserMessage {
        content: ChatCompletionRequestUserMessageContent::Array(vec![
            async_openai::types::ChatCompletionRequestUserMessageContentPart::ImageUrl(image_content),
        ]),
        name: None,
    };

    let request = CreateChatCompletionRequestArgs::default()
        .model("gpt-4o")
        .max_tokens(1024_u16)
        .messages([
            ChatCompletionRequestMessage::System(system_message),
            ChatCompletionRequestMessage::User(user_message),
        ])
        .build()?;

    let response = client.chat().create(request).await?;
    
    Ok(response.choices[0].message.content.clone().unwrap_or_default())
}

/// Get the final answer to math questions with step-by-step working
pub async fn get_final_answer(image_b64: &str) -> Result<String, Box<dyn std::error::Error>> {
    let api_key = env::var("OPENAI_API_KEY")
        .map_err(|_| "OpenAI API key is not set.")?;

    let config = OpenAIConfig::new().with_api_key(api_key);
    let client = Client::with_config(config);

    let system_message = ChatCompletionRequestSystemMessage {
        content: ChatCompletionRequestSystemMessageContent::Text(
            "You are a helpful assistant that guides Year 7 to 10 high school students through math questions. You are to work these questions out step by step and double check your answers, after you have finished this you a to provide ONLY YOUR FINAL ANSWER to the Student, no other junk no thinking just the final answer. You are to respond in PLAIN MARKDOWN! And nothing else, Math Symbols should be in PLAIN text! Example: Prompt: What is 2^5 Response: 32".to_string()
        ),
        name: None,
    };

    // Handle both raw base64 and data URLs
    let image_url = if image_b64.starts_with("data:") {
        image_b64.to_string()
    } else {
        format!("data:image/jpeg;base64,{}", image_b64)
    };

    let image_content = ChatCompletionRequestMessageContentPartImage {
        image_url: ImageUrl {
            url: image_url,
            detail: None,
        },
    };

    let user_message = ChatCompletionRequestUserMessage {
        content: ChatCompletionRequestUserMessageContent::Array(vec![
            async_openai::types::ChatCompletionRequestUserMessageContentPart::ImageUrl(image_content),
        ]),
        name: None,
    };

    let request = CreateChatCompletionRequestArgs::default()
        .model("gpt-4o")
        .max_tokens(512_u16)
        .messages([
            ChatCompletionRequestMessage::System(system_message),
            ChatCompletionRequestMessage::User(user_message),
        ])
        .build()?;

    let response = client.chat().create(request).await?;
    
    Ok(response.choices[0].message.content.clone().unwrap_or_default())
}
