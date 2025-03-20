import tkinter as tk
from PIL import Image, ImageTk
from pynput import mouse, keyboard
import math
import threading
import sys  # Added to handle command-line arguments

class DuckWidget:
    def __init__(self, speed=500):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True, '-alpha', 0.9, '-transparentcolor', 'white')
        self.xy = [0, 0]
        self.moving = False
        self.speed = speed  # This will now be set by the passed speed_mode
        self.running = True

        # Load duck images with error handling
        try:
            self.duck_images = {
                d: ImageTk.PhotoImage(Image.open(f"{d}.png").convert("RGBA"))
                for d in ('north', 'south', 'east', 'west')
            }
            self.current_direction = 'north'
        except Exception as e:
            print(f"Error loading images: {e}")
            self.root.destroy()
            return

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=64, height=64, highlightthickness=0, bg='white')
        self.canvas.pack()
        self.duck = self.canvas.create_image(32, 32, anchor=tk.CENTER, image=self.duck_images[self.current_direction])
        self.root.geometry("64x64+0+0")
        self.root.bind("<F6>", lambda _: self.root.attributes('-topmost', True))

        # Start listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.root.mainloop()

    def on_click(self, x, y, button, pressed):
        if pressed and not self.moving and self.running:
            self.xy = [x, y]
            self.moving = True
            self.determine_direction(x, y)
            threading.Thread(target=self.move_duck, daemon=True).start()

    def determine_direction(self, click_x, click_y):
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()
        delta_x, delta_y = click_x - (current_x + 32), click_y - (current_y + 32)

        # Determine direction based on dominant axis
        if abs(delta_x) > abs(delta_y):
            self.current_direction = 'east' if delta_x > 0 else 'west'
        else:
            self.current_direction = 'south' if delta_y > 0 else 'north'

        self.canvas.itemconfig(self.duck, image=self.duck_images[self.current_direction])

    def on_key_press(self, key):
        if key == keyboard.Key.f6:
            self.running = False
            self.root.destroy()
            self.mouse_listener.stop()  # Stop the mouse listener
            self.keyboard_listener.stop()  # Stop the keyboard listener

    def move_duck(self):
        target_x, target_y = self.xy[0] - 32, self.xy[1] - 32
        self.animate_duck(target_x, target_y)
        self.moving = False

    def animate_duck(self, target_x, target_y):
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()
        distance = math.hypot(target_x - current_x, target_y - current_y)
        if distance == 0:
            return

        steps = max(1, int(distance / self.speed * 60))
        dx, dy = (target_x - current_x) / steps, (target_y - current_y) / steps

        for _ in range(steps):
            if not self.running:
                return
            current_x += dx
            current_y += dy
            self.root.geometry(f"+{int(current_x)}+{int(current_y)}")
            self.root.update_idletasks()
            self.root.after(16)  # ~60 FPS

        self.root.geometry(f"+{target_x}+{target_y}")

if __name__ == "__main__":
    # Check if a speed_mode argument is provided, otherwise use default
    if len(sys.argv) > 1:
        try:
            speed_mode = int(sys.argv[1])  # Convert the passed argument to an integer
            print(f"Starting DuckWidget with speed: {speed_mode}")
        except ValueError:
            print("Invalid speed mode provided. Using default speed of 500.")
            speed_mode = 500
    else:
        speed_mode = 500  # Default speed if no argument is passed

    # Instantiate DuckWidget with the speed_mode
    DuckWidget(speed=speed_mode)