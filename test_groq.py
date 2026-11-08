"""Optional manual connectivity check for the Groq API.

Run explicitly with ``python test_groq.py`` after setting GROQ_API_KEY.
Importing this module does not make a network request.
"""

import os


def main():
    from openai import OpenAI

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("Set GROQ_API_KEY before running this manual check.")

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "سلام! فقط بنویس: connected."}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
