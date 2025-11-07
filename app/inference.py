import os
from functools import lru_cache

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

MODEL_ID = os.getenv("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")


@lru_cache(maxsize=1)
def get_generator():
    """
    Lazy-load the HF pipeline once per process.
    Assumes GPU drivers / torch with CUDA are already installed.
    """
    print(f"[INFO] Loading model: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype="auto",
    )

    gen = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )
    print("[INFO] Model loaded.")
    return gen


def build_prompt(user_message: str) -> str:
    system_prompt = (
        "You are a helpful, concise assistant. "
        "Keep answers short and easy to understand."
    )
    return f"{system_prompt}\n\nUser: {user_message}\nAssistant:"


def generate_reply(user_message: str) -> str:
    generator = get_generator()
    prompt = build_prompt(user_message)

    outputs = generator(
        prompt,
        max_new_tokens=256,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
    )
    full_text = outputs[0]["generated_text"]

    split_token = "Assistant:"
    if split_token in full_text:
        return full_text.split(split_token, 1)[1].strip()
    return full_text.strip()