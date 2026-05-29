from openai import OpenAI

client = OpenAI(
    api_key="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"
)

response = client.chat.completions.create(

    model="gpt-4.1-mini",

    messages=[
        {
            "role": "user",
            "content": "Hello AI"
        }
    ]
)

print(
    response.choices[0].message.content
)