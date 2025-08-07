from config import OPENAI_API_KEY, ROOT_API_KEY
from src.backend.openai import get_step_by_step_guidance, get_final_answer
from src.backend.database import init_db, check_api_key, add_api_key as db_add_api_key

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum


class RequestType(str, Enum):
    step_by_step = "step_by_step"
    final_answer = "final_answer"


class MathsAssistantRequest(BaseModel):
    api_key: str
    image_b64: str
    request_type: RequestType


class AddApiKeyRequest(BaseModel):
    api_key: str
    root_api_key: str


# Initialize DB once at startup
init_db()

app = FastAPI()


@app.post("/maths-assistant/api")
async def maths_assistant_api(request: MathsAssistantRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key is not set. Please contact the server administrator.",
        )

    if not check_api_key(request.api_key):
        raise HTTPException(
            status_code=401, detail="Invalid API key. Please provide a valid key."
        )

    if request.request_type == RequestType.step_by_step:
        guidance = get_step_by_step_guidance(request.image_b64)
        return {"step_by_step_guidance": guidance}

    elif request.request_type == RequestType.final_answer:
        final_answer = get_final_answer(request.image_b64)
        return {"final_answer": final_answer}

    # This is just a fallback; RequestType enforces this already.
    raise HTTPException(
        status_code=400,
        detail="Invalid request type. Use 'step_by_step' or 'final_answer'.",
    )


@app.post("/maths-assistant/api/add-key")
async def add_api_key_route(request: AddApiKeyRequest):
    if request.root_api_key == ROOT_API_KEY:
        if not request.api_key or not request.api_key.strip():
            raise HTTPException(status_code=400, detail="API key cannot be empty.")

        if db_add_api_key(request.api_key):
            return {"message": "API key added successfully."}
        else:
            raise HTTPException(status_code=409, detail="API key already exists.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
