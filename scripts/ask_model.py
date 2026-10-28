"""Send data/llm/prompt.md to Claude once and save the reply exactly as it came back.

This is how data/llm/answer.md was made. The book only reads the saved answer and never calls a
model, so building it needs no API key and gives the same output every time.

Run from the repository root, with your key in the ANTHROPIC_API_KEY environment variable:
    python scripts/ask_model.py
Needs the anthropic package (pip install anthropic). Running it again replaces the saved answer,
and the "Check the citations" chapter will then report on the new one.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import anthropic

MODEL = "claude-haiku-5-5"  # a small, cheap model, the kind you would run over many threads
LLM_DIR = Path(__file__).resolve().parent.parent / "data" / "llm"


def main():
    prompt = (LLM_DIR / "prompt.md").read_text(encoding="utf-8")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        # One pass, no extended thinking: the answer you would get from a quick API call.
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason != "end_turn":
        raise SystemExit(f"stopped early: {response.stop_reason}")
    answer = "".join(block.text for block in response.content if block.type == "text")
    (LLM_DIR / "answer.md").write_text(answer, encoding="utf-8")
    run = {
        "model": response.model,
        "thinking": "disabled",
        "asked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    (LLM_DIR / "answer.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(f"saved {len(answer)} characters from {response.model}")


if __name__ == "__main__":
    main()
