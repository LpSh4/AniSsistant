import json
import schedule
import time
from plyer import notification
from datetime import datetime, timedelta

# File to store notifications
NOTIFICATION_FILE = "notifications.json"


def load_notifications():
    """Load notifications from the JSON file."""
    try:
        with open(NOTIFICATION_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_notifications(notifications):
    """Save notifications to the JSON file."""
    with open(NOTIFICATION_FILE, 'w') as file:
        json.dump(notifications, file, indent=4)


def plan_notification(notification_datetime, content):
    """Schedule a notification for a specific date and time."""

    def notify():
        notification.notify(
            title="Reminder",
            message=content,
            timeout=10  # Notification stays for 10 seconds
        )
        # Remove the job after it has been executed
        schedule.clear(f"notif_{notification_datetime.strftime('%Y%m%d%H%M%S')}")

    # Calculate delay until the notification time
    now = datetime.now()
    if notification_datetime > now:
        delay = (notification_datetime - now).total_seconds()
        # Schedule the notification after the calculated delay
        schedule.every(delay).seconds.do(notify).tag(f"notif_{notification_datetime.strftime('%Y%m%d%H%M%S')}")


def check_and_schedule_notifications():
    """Check all notifications from the JSON file and schedule them."""
    notifications = load_notifications()
    for notif in notifications:
        notification_datetime = datetime.strptime(f"{notif['date']} {notif['time']}", "%m.%d.%Y %H:%M")
        plan_notification(notification_datetime, notif['content'])


def add_new_notification(date_time, content):
    """Add a new notification based on provided arguments."""
    try:
        # Validate the datetime format
        dt = datetime.strptime(date_time, "%m.%d.%Y %H.%M")
        notification_time = dt.strftime("%H:%M")  # Extract time in HH:MM format
        notification_date = dt.strftime("%m.%d.%Y")

        # Save the notification to the JSON file
        notifications = load_notifications()
        notifications.append({
            "date": notification_date,
            "time": notification_time,
            "content": content
        })
        save_notifications(notifications)

        # Schedule the notification immediately
        plan_notification(dt, content)
        print("Notification planned successfully!")
    except ValueError:
        print("Invalid datetime format. Please use MM.DD.YYYY HH.MM.")


def run_notifications(stop_event):
    """Run the scheduler in the background until stop_event is set."""
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def schedule_and_run_notifications(stop_event):
    """Check existing notifications, schedule them, and run the scheduler."""
    check_and_schedule_notifications()
    run_notifications(stop_event)