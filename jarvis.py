from flask import Flask, render_template, request, jsonify
import pyautogui
import time
import webbrowser
import keyboard
import pyperclip
import datetime
import time
import os
import datetime
import webbrowser
import pyautogui
import webbrowser
import keyboard
import json
import random
import pyperclip
import pygame
import speech_recognition as sr
from time import sleep
from bardapi import BardCookies
import threading
from pushbullet import Pushbullet
import win32com.client
import numpy as np
import cv2
import replicate
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('chat.html')


mute_status = False


@app.route("/get", methods=["POST"])
def chat():
    global mute_status
    msg = request.form["msg"]

    if "mute" in msg:
        mute_status = True
        return jsonify({'message': f'Mute status changed to {mute_status}'})

    elif "speak" in msg:
        mute_status = False
        return jsonify({'message': f'Mute status changed to {mute_status}'})

    return jsonify({'message': get_Chat_response(msg)})


voice_command_thread = None
stop_voice_command_flag = threading.Event()


@app.route("/start_voice_command", methods=["POST"])
def start_voice_command():
    global voice_command_thread, stop_voice_command_flag
    if voice_command_thread is None or not voice_command_thread.is_alive():
        stop_voice_command_flag.clear()
        voice_command_thread = threading.Thread(
            target=run_continuous_voice_command)
        voice_command_thread.start()
        return jsonify({"status": "Voice command started"})
    else:
        return jsonify({"status": "Voice command is already running"})


@app.route("/stop_voice_command", methods=["POST"])
def stop_voice_command():
    global stop_voice_command_flag
    stop_voice_command_flag.set()
    return jsonify({"status": "Voice command stopping"})


def run_continuous_voice_command():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        while not stop_voice_command_flag.is_set():
            print("Listening...")
            try:
                audio = r.listen(source, timeout=10)
                print("Recognizing...")
                voice_query = r.recognize_google(audio, language="en-us")
                print(f"You said: {voice_query.lower()}")

                response = get_Chat_response(voice_query.lower())
                send_response_to_client(response)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(
                    f"Could not request results from Google Speech Recognition service; {e}")


def send_response_to_client(response):
    print(response)


def CookieScrapper():
    webbrowser.open("https://bard.google.com")
    sleep(2)
    pyautogui.click(x=1675, y=51)
    sleep(1)
    pyautogui.click(x=1500, y=149)
    sleep(1)
    pyautogui.click(x=1436, y=80)
    sleep(1)
    keyboard.press_and_release('ctrl + w')

    data = pyperclip.paste()

    try:
        json_data = json.loads(data)
        pass

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")

    SID = "__Secure-1PSID"
    TS = "__Secure-1PSIDTS"
    CC = "__Secure-1PSIDCC"

    SIDValue = next((item for item in json_data if item["name"] == SID), None)
    TSValue = next((item for item in json_data if item["name"] == TS), None)
    CCValue = next((item for item in json_data if item["name"] == CC), None)

    if SIDValue is not None:
        SIDValue = SIDValue["value"]
    else:
        print(f"{SIDValue} not found in the JSON data.")

    if TSValue is not None:
        TSValue = TSValue["value"]
    else:
        print(f"{TSValue} not found in the JSON data.")

    if CCValue is not None:
        CCValue = CCValue["value"]
    else:
        print(f"{CCValue} not found in the JSON data.")

    cookie_dict = {
        "__Secure-1PSID": SIDValue,
        "__Secure-1PSIDTS": TSValue,
        "__Secure-1PSIDCC": CCValue,
    }

    return cookie_dict


def run_cookie_scraper():
    while True:
        global cookie_dict
        cookie_dict = CookieScrapper()
        global bard
        bard = BardCookies(cookie_dict=cookie_dict)

        time.sleep(600)


cookie_scraper_thread = threading.Thread(target=run_cookie_scraper)
cookie_scraper_thread.start()


def split_and_save_paragraphs(data):
    paragraphs = data.split('\n\n')
    data = paragraphs[:2]
    separator = ', '
    joined_string = separator.join(data)
    return joined_string


def speak(text):
    if "*" in text:
        text = text.replace("*", "")

    engine = win32com.client.Dispatch("SAPI.SpVoice")

    voices = engine.GetVoices()

    engine.Voice = voices.Item(2)

    engine.Speak(text)


def greet():
    current_hour = datetime.datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning, Sir!"

    elif 12 <= current_hour < 17:
        return "Good afternoon, Sir!"

    elif 17 <= current_hour < 21:
        return "Good evening, Sir!"

    else:
        return "Good night, Sir!"


def open_spotify():
    pyautogui.hotkey('ctrl', 'shift', 's')

# def Time():
#     hour = datetime.datetime.now().strftime("%#I")
#     min = datetime.datetime.now().strftime("%M")
#     am_pm = datetime.datetime.now().strftime("%p")
#     return(f"It's {hour} {min} {am_pm}")


# def weather():
#     location = "Chattogram"
#     url = f'https://wttr.in/{location}?format=%t+%c+%w'
#     res = requests.get(url)
#     weather_data = res.text.strip().split(" ")
#     temperature, condition, description = weather_data[0], weather_data[1], " ".join(weather_data[2:])
#     return(f"The weather in {location} is {temperature}. The condition is {condition}. The wind is {description}")

def check_birthday_today():
    with open("friends.json", "r") as file:
        data = json.load(file)

    friends_data = data.get("friends", [])
    today = datetime.date.today().strftime("%Y-%m-%d")

    for friend_info in friends_data:
        if isinstance(friend_info, dict):
            if friend_info.get("birthday", "") == today:
                if mute_status == False:
                    speak(f"It's {friend_info.get('name', '')}'s Birthday! 🎉🎂")
                return f"It's {friend_info.get('name', '')}'s Birthday! 🎉🎂"
    if mute_status == False:
        speak("No birthdays today.")
    return "No birthdays today."


def check_birthday_tomorrow():
    with open("friends.json", "r") as file:
        data = json.load(file)

    friends_data = data.get("friends", [])
    tomorrow = (datetime.date.today() +
                datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    for friend_info in friends_data:
        if isinstance(friend_info, dict):
            if friend_info.get("birthday", "") == tomorrow:
                if mute_status == False:
                    speak(
                        f"It's {friend_info.get('name', '')}'s Birthday tomorrow! 🎉🎂")
                return f"It's {friend_info.get('name', '')}'s Birthday tomorrow! 🎉🎂"
    if mute_status == False:
        speak("No birthdays tomorrow.")
    return "No birthdays tomorrow."


def parse_text_query(query):
    words = query.split()
    reminder_message = query
    is_tomorrow = "tomorrow" in words
    return reminder_message, is_tomorrow


def schedule_reminder(is_tomorrow):
    today = datetime.date.today()
    current_time = datetime.datetime.now().time()

    if is_tomorrow:
        reminder_date = today + datetime.timedelta(days=1)
    else:
        reminder_date = today

    min_hour = max(current_time.hour, 10)
    min_minute = max(current_time.minute, 0)

    reminder_time = datetime.time(random.randint(
        min_hour, 22), random.randint(min_minute, 59))
    return datetime.datetime.combine(reminder_date, reminder_time)


def add_to_json(reminder):
    try:
        with open('reminders.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(reminder)

    with open('reminders.json', 'w') as file:
        json.dump(data, file)


def remove_from_json(reminder):
    try:
        with open('reminders.json', 'r') as file:
            data = json.load(file)
        data.remove(reminder)
        with open('reminders.json', 'w') as file:
            json.dump(data, file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass


def send_pushbullet_notification(api_key, reminder_message):
    pb = Pushbullet(api_key)
    push = pb.push_note("Reminder", reminder_message)


def detect_faces_in_screenshot(scale_percent=50):
    face_cascade = cv2.CascadeClassifier(
        "C:\\Users\\hasin\\Downloads\\haarcascade_frontalface_default (1).xml")

    screenshot = pyautogui.screenshot()

    screenshot.save('screenshot.jpg')

    image = cv2.imread('screenshot.jpg')

    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    faces = face_cascade.detectMultiScale(
        resized_image, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        print("No faces found")
    else:
        if mute_status == False:
            speak(f"Sir, I have detected {len(faces)} faces.")

    return (f"Sir, I have detected {len(faces)} faces.")


sec = 10


def get_Chat_response(query):
    global mute_status
    while True:
        if "birthday" in query.lower() and "today" in query.lower():
            return check_birthday_today()

        elif "birthday" in query.lower() and "tomorrow" in query.lower():
            return check_birthday_tomorrow()

        elif "detect" and "face" in query:
            return detect_faces_in_screenshot()

        elif "class" in query.lower() and "tomorrow" in query.lower():
            with open("class_schedule.json", "r") as file:
                schedule_data = json.load(file)

            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            tomorrow_str = tomorrow.strftime("%Y-%m-%d")

            class_info = next(
                (entry for entry in schedule_data["schedule"] if entry["date"] == tomorrow_str), None)

            if class_info:
                if mute_status == False:
                    speak(
                        f"Tomorrow, you have {class_info['class_name']}. {'Its an exam day.' if class_info['exam'] else 'Its a regular class day.'}")
                return f"Tomorrow, you have {class_info['class_name']}. {'Its an exam day.' if class_info['exam'] else 'Its a regular class day.'}"
            else:
                if mute_status == False:
                    speak("It looks like you don't have class tomorrow.")
                return "It looks like you don't have class tomorrow."

        elif "open" in query:
            query = query.replace("open", "").strip()
            query = query.replace("jarvis", "").strip()
            action = f"Opening {query}"
            web = f"https://{query}.com"
            webbrowser.open(web)
            if mute_status == False:
                speak(action)
            return (action)

        elif "the time" in query:
            hour = datetime.datetime.now().strftime("%#I")
            min = datetime.datetime.now().strftime("%M")
            am_pm = datetime.datetime.now().strftime("%p")
            if mute_status == False:
                speak(f"Sir the time is {hour} {min} {am_pm}")
            return (f"Sir the time is {hour} {min} {am_pm}")

        # elif "temperature" in query.lower():
        #                 search = "temperature in Chattogram"
        #                 url = f"https://www.google.com/search?q={search}"
        #                 r = requests.get(url)
        #                 data = BeautifulSoup(r.text, "html.parser")
        #                 temp = data.find("div", class_="BNeawe").text
        #                 if mute_status == False:
        #                     speak(f"current {search} is {temp}")
        #                 return(f"current {search} is {temp}")

        # elif "weather" in query.lower():
        #                 location = "Chattogram"
        #                 url = f'https://wttr.in/{location}?format=%t+%c+%w'
        #                 res = requests.get(url)
        #                 weather_data = res.text.strip().split(" ")
        #                 temperature, condition, description = weather_data[0], weather_data[1], " ".join(weather_data[2:])
        #                 if mute_status == False:
        #                     speak(f"The current temperature in {location} is {temperature}. The condition is {condition}. The wind is {description}")
        #                 return(f"The current temperature in {location} is {temperature}. The condition is {condition}. The wind is {description}")

        elif "go to" in query or "get to" in query:
            query = query.replace("go to", "").strip()
            query = query.replace("get to", "").strip()
            query = query.replace("I", "").strip()
            query = query.replace("want", "").strip()
            query = query.replace("wanna", "").strip()
            query = query.replace("how", "").strip()
            query = query.replace("long", "").strip()
            query = query.replace("will it", "").strip()
            query = query.replace("take", "").strip()
            query = query.replace("it", "").strip()
            query = query.replace("might", "").strip()
            query = query.replace("me", "").strip()
            query = query.replace("right", "").strip()
            query = query.replace("now", "").strip()
            webbrowser.open("https://www.google.com/maps/dir//23+MPD+Rd,+Chittagong/@22.3403906,91.7781251,17z/data=!4m9!4m8!1m0!1m5!1m1!1s0x30acd93b7536466f:0xa1aabef13b7a2b56!2m2!1d91.7807!2d22.3403906!3e0?entry=ttu")
            time.sleep(5)
            keyboard.write(query)
            keyboard.press_and_release("enter")
            time.sleep(3)
            pyautogui.click(279, 452)

            start_x, start_y = 100, 173
            end_x, end_y = 164, 175

            pyautogui.click(start_x, start_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y)
            pyautogui.mouseUp()

            pyautogui.hotkey("ctrl", "c")
            copied_text = pyperclip.paste()
            pyautogui.hotkey("ctrl", "w")
            if mute_status == False:
                speak(
                    f"Sir, It will take you about {copied_text} to reach {query}")
            return (f"Sir, It will take you about{copied_text} to reach {query}")

        elif "shut down my computer" in query.lower():
            os.system(f'shutdown /s /t {sec}')
            action = "Shutting down computer sir!"
            if mute_status == False:
                speak(action)
            return (action)

        elif "restart my computer" in query.lower():
            os.system(f'shutdown /r /t {sec}')
            action = "Restarting computer sir!"
            if mute_status == False:
                speak(action)
            return (action)

        elif 'stop' in query and 'playback' in query:
            open_spotify()
            sleep(3)
            pyautogui.press('space')
            time.sleep(5)
            action = 'Pausing playback, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif "start" in query and 'playback' in query:
            open_spotify()
            time.sleep(5)
            pyautogui.press('space')
            action = 'Unpausing playback, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif 'next song' in query:
            open_spotify()
            time.sleep(5)
            pyautogui.hotkey('ctrl', 'Right')
            action = 'playing the next song, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif 'repeat' in query and 'playback' in query:
            open_spotify()
            time.sleep(5)
            pyautogui.hotkey('ctrl', 'r')
            action = 'Repeating the song, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif 'skip' in query:
            open_spotify()
            time.sleep(3)
            pyautogui.hotkey("shift", "Right")
            action = 'Skipping track, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif 'go back' in query:
            open_spotify()
            time.sleep(3)
            pyautogui.hotkey("shift", "Left")
            action = 'Going back, Sir!'
            if mute_status == False:
                speak(action)
            return (action)

        elif 'play' in query:
            action = "OK! Here you go!!"
            if mute_status == False:
                speak(action)
            song_name = query.replace("play", "").replace("could you play", "").replace(
                "please play", "").replace("jarvis", "").strip()
            open_spotify()
            time.sleep(8)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(3)
            keyboard.write(song_name)
            keyboard.press_and_release('enter')
            time.sleep(5)
            pyautogui.click(x=499, y=391)
            if mute_status == False:
                speak("Enjoy Sir!!")
            return ("OK! Here you go!!\nEnjoy Sir!!")

        elif 'remind me' in query:
            api_key = "o.5siX5vwfO3LRisGfbfdRchdANJsE3P9A"
            query = query.replace("remind me", "").strip()
            query = query.replace("to", "").strip()
            reminder_message, is_tomorrow = parse_text_query(query)

            if reminder_message:
                scheduled_time = schedule_reminder(is_tomorrow)
                reminder = {"message": reminder_message,
                            "scheduled_time": str(scheduled_time)}

                add_to_json(reminder)
                print(f"Reminder added to reminders.json for {scheduled_time}")

                current_time = datetime.datetime.now()
                time_remaining = (
                    scheduled_time - current_time).total_seconds()

                if time_remaining > 0:
                    print(
                        f"Waiting for {time_remaining} seconds to send the reminder...")
                    time.sleep(time_remaining)

                send_pushbullet_notification(api_key, reminder_message)
                print("Reminder sent via Pushbullet.")

                remove_from_json(reminder)
            else:
                print(
                    "Invalid input. Please use the format: 'remind me to {reminder message}'")

        elif "jarvis" in query:
            replies = ["Yes, sir!", "Yes, boss!", "For you Sir, always.", "At your service, sir.", "Ready and listening, sir.", "Greetings, sir! How may I assist you?",
                       "I'm here, sir. What can I do for you?", "Ready for your command", "How may I be of service, sir?",  "Hello Sir", "Welcome Back, Sir", greet()]
            reply = random.choice(replies)
            if mute_status == False:
                speak(reply)
            return (reply)

        else:
            RealQuestion = str(query)
            results = bard.get_answer(RealQuestion)['content']

            result = split_and_save_paragraphs(results)

            if not mute_status:
                speak(result)

            return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
