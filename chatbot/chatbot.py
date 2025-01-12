import requests
import re
import json

class Chatbot:
    def __init__(self, memory_file="chatbot_memory.json",WEATHER_API_KEY=None, JOKE_API_KEY=None):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        self.WEATHER_API_KEY = WEATHER_API_KEY
        self.JOKE_API_KEY = JOKE_API_KEY

    def chatbot_response(self, user_input):
        patterns = [
            (r"hello|hi|hey", "Hi there! How can I help you?"),
            (r"how are you", "I'm just a bunch of code, but I'm doing great! How about you?"),
            (r"what is your name", "I'm your friendly chatbot. What's your name?"),
            (r"my name is (.+)", self.remember_name),
            (r"what's my name", self.recall_name),
            (r"tell me a joke", self.tell_joke),
            (r"what's the weather in (.+)", self.tell_weather),
            (r"bye|goodbye", "Goodbye! Have a great day!"),
            (r"help|assist", "Sure, I'm here to help. Ask me anything!")
        ]

        for pattern, response in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if callable(response):
                    return response(match)
                return response

        return "I'm sorry, I didn't understand that. Can you rephrase?"

    def remember_name(self, match):
        name = match.group(1)
        self.memory["name"] = name
        self.save_memory()
        return f"Nice to meet you, {name}!"

    def recall_name(self, match):
        if "name" in self.memory:
            return f"Your name is {self.memory['name']}!"
        return "I don't think you've told me your name yet."

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f)

    def load_memory(self):
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def tell_joke(self, _):
        joke = self.get_joke()
        return joke
     
    def tell_weather(self, match):
       location = match.group(1).strip()
       api_key = self.WEATHER_API_KEY
       url = "http://api.weatherapi.com/v1/current.json"
       params ={
          "key":api_key,
          "q":location,
       }
       
       try:
          response = requests.get(url, params=params)
          if response.status_code == 200:
             data = response.json()
             city = data['location']['name']
             country = data['location']['country']
             temp = data['current']['temp_c']
             condition = data['current']['condition']['text']
             return f"The current weather in {city}, {country} is {temp}°C with {condition}."
          else:
            return f"Sorry, I couldn't fetch the weather for '{location}'. Please check the location name or try again."
       except Exception as e:
          return f"Error fetching weather data: {str(e)}"
       
    def get_joke(self):
       api_key = self.JOKE_API_KEY
       url = "https://api.humorapi.com/jokes/random"
       params = {
          "api-key":api_key,
       }
       
       try:
          response = requests.get(url, params=params)
          response.raise_for_status()

          joke_data = response.json()
          
          if "joke" in joke_data:
             return joke_data["joke"]
          else:
             return "No joke found in the response. Please try again later."
       except requests.exceptions.RequestException as e:
          return f"Error fetching joke: {str(e)}"
       except ValueError:
          return "Error: Invalid response from the API. Please try again later."