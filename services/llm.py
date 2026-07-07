"""
services/llm.py
Gemini LLM wrapper used by mcp_server/server.py and agents.
"""
import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def llm_enabled() -> bool:
    return bool(api_key)


def call_gemini(prompt: str) -> str:
    if not api_key:
        print("Gemini API key missing.")
        return ""
    try:
        print("===== GEMINI CALLED =====")
        model = genai.GenerativeModel(MODEL)

        try:
            prompt_tokens = model.count_tokens(prompt)
            print("Gemini input prompt tokens:", prompt_tokens.total_tokens)
        except Exception as token_error:
            print("Could not count prompt tokens:", token_error)

        resp  = model.generate_content(prompt)
        usage = getattr(resp, "usage_metadata", None)
        if usage:
            print("===== GEMINI TOKEN USAGE =====")
            print("Prompt tokens :", getattr(usage, "prompt_token_count", None))
            print("Output tokens :", getattr(usage, "candidates_token_count", None))
            print("Total tokens  :", getattr(usage, "total_token_count", None))
            print("==============================")

        text = getattr(resp, "text", None)
        if text:
            return text.strip()

        parts = []
        for candidate in getattr(resp, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", "")
                if part_text:
                    parts.append(part_text)
        return "".join(parts).strip()

    except Exception as e:
        print("Gemini error:", e)
        return ""


def extract_json(text: str):
    """Parse a JSON object/array from model output (handles ``` fences)."""
    if not text:
        return None
    t = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"(\{.*\}|\[.*\])", t, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
    return None
