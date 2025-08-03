from config import OPENAI_API_KEY
from openai import OpenAI
from .screenshot import encode_image_to_base64

client = OpenAI(api_key=OPENAI_API_KEY)


def get_step_by_step_guidance(image_path):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set.")

    image_b64 = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that guides Year 7 to 10 high school students, you will help them answer their math questions, you will not provide the final answer, you will only provide step-by-step guidance using clear and simple explanations suitable for their level. You WILL NOT PROVIDE THE FINAL ANSWER!"
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    }
                ],
            },
        ],
    )
    return response.choices[0].message.content


def get_final_answer(image_path):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set.")

    image_b64 = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that provides the final answer to Year 7 to 10 high school math questions. "
                    "Do not provide explanations or steps, just the direct answer."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    }
                ],
            },
        ],
    )
    return response.choices[0].message.content
