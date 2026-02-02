import os
import requests
import datetime

class FarmAI:
    def __init__(self):
        # We will look for GEMINI_API_KEY in environment variables
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def analyze_logs(self, logs):
        """
        Analyzes a list of Daily Logs (Notes) and provides insights.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "AI API Key missing. Please set GEMINI_API_KEY in .env file."
            }
        
        # Prepare the prompt
        log_text = "\n".join([f"- {log.created_at.strftime('%Y-%m-%d')}: {log.content}" for log in logs])
        prompt = f"""
        You are an expert Agronomist AI. Analyze the following farm logs from the last 7 days and provide:
        1. A summary of activities.
        2. Potential risks (pests, weather, delays).
        3. Recommended next steps for the farmer.
        
        Logs:
        {log_text}
        
        Keep the response concise and formatted in HTML (using <ul>, <li>, <strong> tags).
        """
        
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            headers = {'Content-Type': 'application/json'}
            params = {'key': self.api_key}
            
            response = requests.post(self.api_url, json=payload, headers=headers, params=params)
            response_data = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in response_data:
                ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
                return {"status": "success", "content": ai_text}
            else:
                return {"status": "error", "message": "No response from AI"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask_crop_doctor(self, crop_name, sowing_date=None):
        """
        Provides Advice for a specific Crop.
        """
        if not self.api_key:
            return {"status": "error", "message": "AI Key Missing"}
            
        context = f"Planted on {sowing_date}" if sowing_date else "Planning to plant"
        prompt = f"""
        You are an expert Agronomist. The farmer is asking about '{crop_name}' ({context}).
        Provide a concise HTML response covering:
        1. 🐛 Common Pests & Diseases to watch out for NOW.
        2. 💧 Watering & Care tips.
        3. ⏳ Estimated Harvest time from now.
        
        Keep it brief and practical. Use bullet points.
        """
        
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {'Content-Type': 'application/json'}
            params = {'key': self.api_key}
            
            response = requests.post(self.api_url, json=payload, headers=headers, params=params)
            data = response.json()
            
            if 'candidates' in data:
                return {"status": "success", "content": data['candidates'][0]['content']['parts'][0]['text']}
            return {"status": "error", "message": "AI Silent"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def recommend_crops(self, area, season, location="India"):
        """
        Suggests profitable crops based on season and area.
        """
        if not self.api_key:
            return {"status": "error", "message": "AI Key Missing"}
            
        prompt = f"""
        Act as an Agriculture Business Consultant.
        The user has {area} of land available in {season} (Location: {location}).
        
        Suggest 3 most profitable vegetable/crop options.
        For each option, provide:
        1. 💰 **Estimated Profit Potential** (High/Med/Low)
        2. ⏳ **Duration** (Days to harvest)
        3. 💡 **Why this crop?** (Market demand, weather suitability)
        
        Format the response as a clean HTML table or list.
        """
        
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {'Content-Type': 'application/json'}
            params = {'key': self.api_key}
            
            response = requests.post(self.api_url, json=payload, headers=headers, params=params)
            data = response.json()
            
            if 'candidates' in data:
                return {"status": "success", "content": data['candidates'][0]['content']['parts'][0]['text']}
            return {"status": "error", "message": "AI Silent"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_crop_duration(self, crop_name):
        """
        Returns the estimated duration in days for a crop.
        """
        if not self.api_key:
            return None
            
        prompt = f"""
        How many days does '{crop_name}' typically take from sowing to harvest?
        Return ONLY the number of days as an integer (e.g. 90). 
        If it varies, give a safe average.
        """
        
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {'Content-Type': 'application/json'}
            params = {'key': self.api_key}
            
            response = requests.post(self.api_url, json=payload, headers=headers, params=params)
            data = response.json()
            
            if 'candidates' in data:
                text = data['candidates'][0]['content']['parts'][0]['text']
                # Extract number from text
                import re
                match = re.search(r'\d+', text)
                if match:
                    return int(match.group())
            return None
        except:
            return None

# Singleton instance
ai_advisor = FarmAI()
