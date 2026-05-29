from google import genai

client = genai.Client(
    api_key="AIzaSyCKv7qfN7fJZ0C4Ng77mUY54tSBfVd4hrU"
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Hello AI"
)

print(response.text)