import os
from functools import lru_cache

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

MODEL_ID = os.getenv("MODEL_ID")


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
    tokenizer = generator.tokenizer
    messages = [
        {
            "role": "system",
            "content": "You are a helpful, concise assistant. Keep answers short and easy to understand.",
        },
        {"role": "user", "content": user_message},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    outputs = generator(
        prompt,
        max_new_tokens=256,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        return_full_text=False,
    )
    return outputs[0]["generated_text"].strip()
