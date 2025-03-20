import KeyboardSounds as kbs
import WalkingCreature as wkcrt
import threading
import Notifications
import Supports as sp

def main_script():
    active_threads = {}
    stop_events = {}

    while True:
        print(f'\n {"   " * 12}Welcome to the Testing Grounds!')
        print('1 ==== Running game (already running)\n'
              '2 ==== Keyboard sounds\n'
              '3 ==== Notifications\n'
              '69 === Start/Stop Background Tasks\n'
              '85 === Exit')
        user = sp.turnint(input('Enter the number of script you would test: '))

        if user == 1:
            print("Duck is already running in the main thread!")

        elif user == 2:
            if input('Use standard values? ') in ['y', 'Y']:
                rules = [
                    r'C:\Eggs\Projects\AniSsistant\key_sound.mp3',
                    r"C:\Eggs\Projects\AniSsistant\mouse_sound.mp3",
                    False,
                    False
                ]
            else:
                rules = [
                    input('Enter the key sound path: '),
                    input('Enter the click sound path: '),
                    False if input('Exclude keyboard? ') in ['n', 'N'] else True,
                    False if input('Exclude mouse? ') in ['n', 'N'] else True
                ]
            thread_name = "keyboard_sounds"
            active_threads[thread_name] = threading.Thread(
                target=kbs.play_sounds, args=rules, daemon=True
            )
            active_threads[thread_name].start()
            print(f"{thread_name} started.")

        elif user == 3:
            print("Enter the date and time (format: MM.DD.YYYY HH.MM):")
            date_time = input("DateTime: ")
            content = input("Content: ")
            Notifications.add_new_notification(date_time, content)
            if "notifications" not in active_threads or not active_threads["notifications"].is_alive():
                stop_event = threading.Event()
                stop_events["notifications"] = stop_event
                thread_name = "notifications"
                active_threads[thread_name] = threading.Thread(
                    target=Notifications.schedule_and_run_notifications, args=(stop_event,), daemon=True
                )
                active_threads[thread_name].start()

        elif user == 69:
            print("Active background tasks:")
            for name, thread in active_threads.items():
                status = "Running" if thread.is_alive() else "Stopped"
                print(f"- {name}: {status}")
            task_to_stop = input("Enter the name of the task to stop (or press Enter to skip): ").strip()
            if task_to_stop in stop_events and active_threads[task_to_stop].is_alive():
                print(f"Stopping {task_to_stop}...")
                stop_events[task_to_stop].set()
                print(f"{task_to_stop} will stop after completing its current iteration.")
            else:
                print(f"No active task named '{task_to_stop}' found.")

        elif user == 85:
            print("Exiting...")
            for event in stop_events.values():
                event.set()
            break

        else:
            print('Invalid input. Try again.')

if __name__ == "__main__":
    wkcrt.let_girl_out(50, main_script)