from pygame.mixer import Sound
from pynput import keyboard, mouse
import pygame, threading, sys
import Supports as sp

# Global variables
play_sounds_enabled = False
stop_program = False  # Flag to stop the program
key_states = {}  # Tracks key states
mouse_states = {}  # Tracks mouse button states

def toggle_sound_playback():
    global play_sounds_enabled
    play_sounds_enabled = not play_sounds_enabled

def play_sounds(key_sound, click_sound, keyboard_excluded=False, mouse_excluded=False):
    pygame.mixer.init()
    global stop_program, key_states, mouse_states, play_sounds_enabled
    play_sounds_enabled = False
    stop_program = False  # Flag to stop the program
    key_states = {}  # Tracks key states
    mouse_states = {}  # Tracks mouse button states

    # Load sound files
    try:
        key_audio = Sound(sp.resource_path(key_sound))
        mouse_audio = Sound(sp.resource_path(click_sound))
    except Exception as e:
        print(f"Error loading sound files: {e}")
        return

    def on_key_press(key):
        global stop_program
        # Ignore if the key is already pressed
        if key_states.get(key):
            return
        key_states[key] = True

        # Handle hotkeys
        if key == keyboard.Key.f4:
            toggle_sound_playback()
            return
        if key == keyboard.Key.f6:
            stop_program = True
            return

        # Play sound if enabled
        if play_sounds_enabled and not keyboard_excluded:
            sp.play_sound(key_audio)

    def on_key_release(key):
        """Handle key release events."""
        key_states[key] = False

    def on_click(x, y, button, pressed):
        """Handle mouse click events."""
        # Ignore if the button is already pressed
        if mouse_states.get(button) == pressed:
            return
        mouse_states[button] = pressed

        # Play sound if enabled
        if pressed and play_sounds_enabled and not mouse_excluded:
            sp.play_sound(mouse_audio)

    # Start listeners
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_click=on_click)

    try:
        keyboard_listener.start()
        mouse_listener.start()

        # Keep the main thread alive while checking for stop_program flag
        while not stop_program:
            # Sleep briefly to avoid busy-waiting
            threading.Event().wait(0.1)

    finally:
        # Ensure listeners are stopped and joined
        keyboard_listener.stop()
        mouse_listener.stop()

        # Wait for threads to finish
        keyboard_listener.join()
        mouse_listener.join()

        # Clean up Pygame mixer
        pygame.mixer.quit()

if __name__ == "__main__":
    # Check if a speed_mode argument is provided, otherwise use default
    if len(sys.argv) > 1:
        try:
            print(sys.argv)
            key_sound = str(sys.argv[1])
            mouse_sound = str(sys.argv[2])
        except ValueError:
            print("Invalid speed mode provided. Using default values.")
            key_sound = sp.resource_path('sounds//key_sound.mp3')
            mouse_sound = sp.resource_path('sounds//key_sound.mp3')
    else:
        key_sound = sp.resource_path('sounds//key_sound.mp3')
        mouse_sound = sp.resource_path('sounds//key_sound.mp3')
    play_sounds(key_sound, mouse_sound)
