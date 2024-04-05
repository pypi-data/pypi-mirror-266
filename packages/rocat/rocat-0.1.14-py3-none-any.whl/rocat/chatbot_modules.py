# rocat/chatbot.py
from abc import ABC, abstractmethod
from openai import OpenAI
import anthropic

class Chatbot(ABC):
    @abstractmethod
    def set_system_prompt(self, new_prompt):
        pass

    @abstractmethod
    def generate_response(self, user_prompt):
        pass

class OpenAIChatbot(Chatbot):
    def __init__(self, api_key, model="gpt-3.5-turbo", max_tokens=512, temperature=0.7):
        """Initialize the OpenAI chatbot with the given API key, model, and hyperparameters."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = "You are a helpful assistant."

    def set_system_prompt(self, new_prompt):
        """Set the system prompt for the chatbot."""
        self.system_prompt = new_prompt

    def generate_response(self, user_prompt):
        """Generate a response based on the given user prompt."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        return response.choices[0].message.content.strip()

class ClaudeChatbot(Chatbot):
    def __init__(self, api_key, model="claude-3-haiku-20240307", max_tokens=512, temperature=0.7):
        """Initialize the Claude chatbot with the given API key, model, max_tokens, and temperature."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = "You are a helpful assistant."

    def set_system_prompt(self, new_prompt):
        """Set the system prompt for the chatbot."""
        self.system_prompt = new_prompt

    def generate_response(self, user_prompt):
        """Generate a response based on the given user prompt."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
        
