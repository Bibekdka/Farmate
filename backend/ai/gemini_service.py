import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in environment!")
        else:
            genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_farming_advice(self, prompt: str) -> str:
        try:
            # We add a small system prompt to guide it to agricultural context
            full_prompt = f"You are an expert agricultural assistant. Provide a helpful, accurate, and concise answer to the following farming question:\n\n{prompt}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return "I'm sorry, I'm having trouble analyzing that request right now."

# Singleton instance
ai_service = GeminiService()
