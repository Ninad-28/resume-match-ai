import google.generativeai as genai

# PASTE YOUR KEY HERE
GENAI_API_KEY = "AIzaSyDQqMuSj6Sxmi1Nf0ZTOGJlAwnEppdWC2Q"

genai.configure(api_key=GENAI_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")