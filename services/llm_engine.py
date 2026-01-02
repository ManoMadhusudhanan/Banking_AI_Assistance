from openai import OpenAI
import os

# Make sure your API key is set as an environment variable OR paste it here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def smart_llm_reply(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional banking assistant. "
                    "Explain concepts clearly and safely. "
                    "Do not provide financial advice. "
                    "Help with banking terms like NEFT, RTGS, IMPS, loans, credit score, cards, etc."
                )
            },
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content
