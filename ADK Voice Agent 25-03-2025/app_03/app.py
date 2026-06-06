import google.generativeai as genai

genai.configure(api_key="AIzaSyCdzKnGkFIHbZ_m8MMJjc6gAPiFcFjl_ZU")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)