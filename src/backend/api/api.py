from config import OPENAI_API_KEY
from src.backend.openai import (
    get_step_by_step_guidance,
    get_final_answer,
)

from fastapi import FastAPI
from pydantic import BaseModel


class MathsAssistantRequest(BaseModel):
    image_b64: str
    request_type: str


app = FastAPI()


@app.post("/maths-assistant/api")
async def maths_assistant_api(request: MathsAssistantRequest):
    """
    Process the image and return either step-by-step guidance or the final answer.
    Args:
        request (MathsAssistantRequest): Request body with image_b64 and request_type.
    Returns:
        dict: Response containing either step-by-step guidance or the final answer.
    """
    if not OPENAI_API_KEY:
        return {
            "error": "OpenAI API key is not set. Please contact the server administrator."
        }

    if request.request_type == "step_by_step":
        guidance = get_step_by_step_guidance(request.image_b64)
        return {"step_by_step_guidance": guidance}

    elif request.request_type == "final_answer":
        final_answer = get_final_answer(request.image_b64)
        return {"final_answer": final_answer}
    else:
        return {"error": "Invalid request type. Use 'step_by_step' or 'final_answer'."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
