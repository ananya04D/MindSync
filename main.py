import os
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import requests
import openai
import subprocess

from config import apikey, WEATHER_API_KEY, NEWS_API_KEY  # API keys from your config file

# Global chat history string
chatStr = ""

def chat(query):
    global chatStr
    openai.api_key = apikey
    chatStr += f"Ananya: {query}\nMindSync: "

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        response_text = response.choices[0].message['content']
        say(response_text)
        chatStr += f"{response_text}\n"
        return response_text

    except openai.error.RateLimitError:
        say("I have exceeded my API quota. Please try again later.")
        return "Error: Rate limit exceeded."

def play_youtube_song(song_name):
    """Search for the song on YouTube and play it."""
    query = f"https://www.youtube.com/results?search_query={song_name}"
    webbrowser.open(query)
    say(f"Playing {song_name} on YouTube.")

def get_weather(city_name):
    """Get weather information from OpenWeatherMap API."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        # Debug: Print raw API response
        print("Weather API Response:", data)

        if data.get("cod") == 200:
            main = data['main']
            weather_desc = data['weather'][0]['description']
            temperature = main['temp']
            result = (
                f"Weather in {city_name}:\n"
                f"Temperature: {temperature}°C\n"
                f"Condition: {weather_desc.capitalize()}\n"
                f"Humidity: {main['humidity']}%\n"
                f"Pressure: {main['pressure']} hPa"
            )
        else:
            result = f"Sorry, I couldn't find weather information for {city_name}. Reason: {data.get('message', 'No message provided.')}"

        say(result)

    except Exception as e:
        say(f"Error fetching weather information. Exception: {str(e)}")

def get_news():
    """Get top news headlines using NewsAPI and print them while reading."""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Debug: Print raw API response
        print("News API Response:", data)

        if data["status"] == "ok":
            articles = data["articles"][:5]  # Fetch top 5 news articles
            headlines = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles)])
            result = f"Top 5 News Headlines:\n{headlines}"
        else:
            result = "Sorry, I couldn't fetch news at the moment."

        # Print the news headlines
        print(result)

        # Read out the news headlines
        say(result)

    except Exception as e:
        error_message = f"Error fetching news. Exception: {str(e)}"
        say(error_message)
        print(error_message)


def search_wikipedia(query):
    """Open a search query on Wikipedia in the browser."""
    search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={query}"
    webbrowser.open(search_url)
    say(f"Searching Wikipedia for {query}.")

def open_application(app_name):
    """Open specified system application."""
    applications = {
        "camera": "start microsoft.windows.camera:",
        "calendar": "start outlookcal:",
        "calculator": "calc",
        "settings": "start ms-settings:",
        "file explorer": "explorer",
        "edge": "start msedge:",
        "chrome": "start chrome:"
    }
    if app_name in applications:
        subprocess.run(applications[app_name], shell=True)
        say(f"Opening {app_name}.")
    else:
        say(f"Application {app_name} not found.")

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            try:
                query = r.recognize_google(audio, language="en-in")
                return query
            except sr.UnknownValueError:
                return "Sorry, I didn't catch that."
            except sr.RequestError:
                return "Sorry, I'm having trouble with the speech recognition service."
        except sr.WaitTimeoutError:
            return "Sorry, I didn't hear anything."
        except Exception as e:
            return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    print('MindSync - Your Virtual Assistant')
    say("Hello, this is MindSync. I am your virtual assistant. How can I assist you today?")
    while True:
        query = takeCommand().lower()
        if query:  # Only process if there's a query
            # Define the commands that should not use OpenAI API
            non_openai_commands = [
                "play this song",
                "weather in",
                "news",
                "the time",
                "open",
                "search wikipedia"
            ]
            if "play from youtube" in query:
                song_name = query.replace("play from youtube", "").strip()
                play_youtube_song(song_name)

            elif "weather in" in query:
                city_name = query.replace("weather in", "").strip()
                get_weather(city_name)

            elif "news" in query:
                get_news()

            elif "the time" in query:
                hour = datetime.datetime.now().strftime("%H")
                min = datetime.datetime.now().strftime("%M")
                sec = datetime.datetime.now().strftime("%S")
                say(f"The time is {hour} hours {min} minutes and {sec} seconds.")

            elif "open" in query:
                app_name = query.replace("open", "").strip()
                open_application(app_name)

            elif "search wikipedia" in query:
                search_query = query.replace("search wikipedia", "").strip()
                search_wikipedia(search_query)

            elif "exit" in query:
                say("Goodbye! Have a great day!")
                exit()

            elif "reset chat" in query:
                chatStr = ""
                say("Chat history has been reset.")

            else:
                response = chat(query)
                print(f"MindSync: {response}")

    print("MindSync has been terminated.")
