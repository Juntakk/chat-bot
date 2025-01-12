from datetime import datetime
import requests
import re
import json
from langdetect import detect, DetectorFactory
from google.cloud import translate_v2 as translate


class Chatbot:
    def __init__(self, memory_file="chatbot_memory.json",WEATHER_API_KEY=None, JOKE_API_KEY=None, google_translate_key=None):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        self.WEATHER_API_KEY = WEATHER_API_KEY
        self.JOKE_API_KEY = JOKE_API_KEY
        self.translate_client = translate.Client() if google_translate_key else None

    def chatbot_response(self, user_input):
      language = self.detect_language(user_input)
      print(language)
      responses = {
         'en': {
               r"hello|\bhi\b|hey": "Hi there! How can I help you?",
               r"how are you": "I'm just a bunch of code, but I'm doing great! How about you?",
               r"what is your name": "I'm your friendly chatbot. What's your name?",
               r"my name is (.+)": self.remember_name,
               r"what's my name": self.recall_name,
               r"tell me a joke": self.tell_joke,
               r"what's the weather in (.+)": self.tell_weather,
               r"bye|goodbye": "Goodbye! Have a great day!",
               r"help|assist": "Sure, I'm here to help. Ask me anything!",
               r"why should i hire nick": "Because he is the best"
         },
         'fr': {
               r"bonjour|\bsalut\b|allo": "Salut! Comment puis-je vous aider?",
               r"comment ca va": "Je suis juste un tas de code, mais je vais très bien ! Et toi ?",
               r"quel est ton nom": "Je suis votre chatbot amical. Quel est votre nom ?",
               r"mon nom est (.+)": self.remember_name,
               r"quel est mon nom": self.recall_name,
               r"raconte une blague": self.tell_joke,
               r"quel temps fait-il à (.+)": self.tell_weather,
               r"au revoir|bye": "Au revoir! Passez une excellente journée!",
               r"aide|assistance": "Bien sûr, je suis là pour vous aider. Demandez-moi n'importe quoi!",
               r"pourquoi devrais-je embaucher nick": "Parce qu'il est le meilleur"
            }
      }

      if language not in responses:
         language = "en"

      for pattern, response in responses[language].items():
         match = re.search(pattern, user_input, re.IGNORECASE)
         if match:
               # Check if the response is a callable function and call accordingly
               if callable(response):
                  # Check if the function takes only one argument (match)
                  if response.__code__.co_argcount == 2:
                     return response(match)
                  # If the function requires more, pass both match and language
                  return response(match, language)
               return response

      return self.translate_response("I'm sorry, I didn't understand that. Can you rephrase?", language)

    def detect_language(self, user_input):
        try:
            language = detect(user_input)

            if language == "hr" and "bonjour" in user_input.lower():
                return "fr"
            # if language == "ca" or language == "cy" or language == "fi" or language == "it":
            #     return "fr"
            return language
        except:
            return "en"

    def translate_response(self, text, target_language):
        if not self.translate_client:
            return text
        
        try:
            translation = self.translate_client.translate(text, target_language=target_language)
            return translation["translatedText"]
        except Exception as e:
            return f"Translation error: {str(e)}"
    
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
             time_of_day = self.get_time_of_day()
             return f"The current weather in {city}, {country} is {temp}°C with {condition}. It's {time_of_day}"
          else:
            return f"Sorry, I couldn't fetch the weather for '{location}'. Please check the location name or try again."
       except Exception as e:
          return f"Error fetching weather data: {str(e)}"
    
    def get_time_of_day(self):    
      current_hour = datetime.now().hour
      if current_hour < 12:
          return "morning"
      elif current_hour < 18:
          return "afternoon"
      else:
          return "evening"
      
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