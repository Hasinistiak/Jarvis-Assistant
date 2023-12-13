from time import sleep
import schedule
import datetime
import json
from pushbullet import Pushbullet
from plyer import notification

API_KEY = "o.mHWMK4ECvzBytldR0mEDohV7z0dw0YbI"
pb = Pushbullet(API_KEY)

last_sent_date = None  

def send_birthday_notification(username):
    # Pushbullet notification
    notification_title_pb = f"It's {username}'s Birthday"
    notification_text_pb = f"Go and wish {username}!"
    pb.push_note(notification_title_pb, notification_text_pb)

    # PC notification
    notification_title_pc = f"It's {username}'s Birthday"
    notification_text_pc = f"GO and Wish {username}!"
    notification.notify(
        title=notification_title_pc,
        message=notification_text_pc,
        app_icon=None,  # e.g., 'C:\\icon_32x32.ico'
        timeout=10,  # seconds
    )

def load_friends_schedule():
    with open("friends.json", "r") as file:
        friends_schedule = json.load(file)
    return friends_schedule

def delete_used_birthdays(friends_list):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M")

    for friend in friends_list[:]:
        if friend["birthday"] == current_date and friend["time"] <= current_time:
            friends_list.remove(friend)

    return friends_list

def update_friends_schedule(friends_schedule):
    with open("friends.json", "w") as file:
        json.dump({"friends": friends_schedule}, file, indent=2)

def check_schedule():
    global last_sent_date

    current_date = datetime.datetime.now().date()

    if last_sent_date is not None and last_sent_date == current_date:
        return

    friends_schedule = load_friends_schedule()["friends"]
    friends_schedule = delete_used_birthdays(friends_schedule)

    for friend in friends_schedule:
        birthday_date = datetime.datetime.strptime(friend["birthday"], "%Y-%m-%d")
        birthday_time = datetime.datetime.strptime(friend["time"], "%H:%M")

        current_datetime = datetime.datetime.now()
        current_time = current_datetime.time()

        if current_date == birthday_date.date() and current_time >= birthday_time.time():
            print(f"Birthday Found!")
            send_birthday_notification(friend["name"])
            last_sent_date = current_date

    update_friends_schedule(friends_schedule)

schedule.every(1).minutes.do(check_schedule)

if __name__ == "__main__":
    try:
        while True:
            schedule.run_pending()
            sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")
