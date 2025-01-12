# chatbot/views.py
from django.http import JsonResponse
from django.shortcuts import render
from .chatbot import Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

chatbot_instance = Chatbot(
    WEATHER_API_KEY=os.getenv("WEATHER_API_KEY"),
    JOKE_API_KEY=os.getenv("JOKE_API_KEY")
)

from django.http import JsonResponse
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.template.loader import render_to_string

def chatbot_home(request):
    if "conversation" not in request.session:
        request.session["conversation"] = []

    if request.method == "POST":
        user_input = request.POST.get("user_input", "")
        chatbot_response = chatbot_instance.chatbot_response(user_input)  # Get the bot's response

        # Store the conversation in the session
        request.session["conversation"].append({"user": user_input, "bot": chatbot_response})
        request.session.modified = True

        # Check if the request is AJAX by inspecting the header
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "response": chatbot_response,
                "user_input": user_input
            })

        # If it's not an AJAX request, render the page normally
        return render(request, "chatbot/home.html", {
            "conversation": request.session["conversation"]
        })
    
    # If it's a GET request, return the conversation history
    return render(request, "chatbot/home.html", { "conversation": request.session["conversation"] })


