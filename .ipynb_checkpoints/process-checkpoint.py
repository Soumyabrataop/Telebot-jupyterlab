from openai import OpenAI
import os

def call_sambanova_chat(prompt, api_key):
    # Validate API key
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        raise ValueError("API key is required and cannot be empty or placeholder value")
    
    # Validate prompt
    if not prompt or prompt.strip() == "" or prompt == "Your prompt here":
        raise ValueError("Prompt is required and cannot be empty or placeholder value")
    

    with open('systemprompt.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read()

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.sambanova.ai/v1",
    )

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        top_p=0.1
    )

    return response.choices[0].message.content