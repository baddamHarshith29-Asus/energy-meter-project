import os
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
            self.openai_client = None
            self.model = "llama-3.1-8b-instant"
            print("AI Service: Using Native Groq SDK")
        elif self.openai_key and self.openai_key != 'your_api_key_here':
            self.openai_client = OpenAI(api_key=self.openai_key)
            self.groq_client = None
            self.model = "gpt-3.5-turbo"
            print("AI Service: Using OpenAI")
        else:
            self.groq_client = None
            self.openai_client = None
            self.model = ""

    def get_explanation(self, data_context):
        if not self.groq_client and not self.openai_client:
            return "AI Explanation is unavailable without an API key (OpenAI or Groq). Please check your .env file."
            
        prompt = f"Explain the following energy usage pattern and provide optimization tips: {data_context}"
        
        try:
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def chat_assistant(self, user_query, history=None, context=None):
        if not self.groq_client and not self.openai_client:
            return "Chat Assistant is currently offline. Add GROQ_API_KEY or OPENAI_API_KEY to your backend/.env to enable intelligence."
            
        messages = list(history) if history else []
        
        # Always inject simulation context as a system message if available.
        # This ensures the AI always knows about the current simulation
        # REGARDLESS of how many messages are already in the chat history.
        if context:
            simulated = context.get('simulated', {})
            baseline = context.get('baseline', {})
            system_content = (
                f"You are an expert energy optimization AI assistant. "
                f"The user has just run a simulation with the following results:\n"
                f"- Baseline Monthly Cost: ${baseline.get('bill', 0):.2f} ({baseline.get('units', 0):.1f} kWh)\n"
                f"- Simulated Monthly Cost: ${simulated.get('bill', 0):.2f} ({simulated.get('units', 0):.1f} kWh)\n"
                f"- Projected Monthly Savings: ${simulated.get('savings', 0):.2f}\n"
                f"- Efficiency Score: {simulated.get('score', 0)}/100\n"
                f"Always refer to these specific numbers in your answers. Be concise and practical."
            )
            # Prepend system message — replace any existing system message if present
            messages = [m for m in messages if m.get('role') != 'system']
            messages.insert(0, {"role": "system", "content": system_content})
            
        messages.append({"role": "user", "content": user_query})
        
        try:
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Error: {str(e)}"
