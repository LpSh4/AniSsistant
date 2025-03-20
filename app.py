import tkinter as tk
import tkinter.messagebox
import customtkinter as CTk
import cv2, threading, Supports as sp
from PIL import Image, ImageTk
import subprocess

# Настройка внешнего вида для customtkinter
CTk.set_appearance_mode("light")
CTk.set_default_color_theme("blue")

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("400x300+500+200")
        self.canvas = tk.Canvas(root, width=400, height=300, bg="white")
        self.canvas.pack()

        try:
            self.cap = cv2.VideoCapture(r"D:\groupppro\logo.mp4")
            if not self.cap.isOpened():
                raise Exception("Не удалось открыть видеофайл для заставки.")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.close_splash()
            return

        self.play_video()

    def play_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(200, 150, image=img_tk)
            self.canvas.image = img_tk
            self.root.after(33, self.play_video)
        else:
            self.cap.release()
            self.close_splash()

    def close_splash(self):
        self.root.destroy()
        app = App()
        app.mainloop()

class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x450")
        self.resizable(False, False)
        self.title("Anissistant")
        self.notifications_list = []
        self.walking_creature_process = None  # To track the WalkingCreature subprocess
        self.keyboard_sounds_process = None  # To track the KeyboardSounds subprocess

        try:
            self.bg_image = CTk.CTkImage(
                dark_image=Image.open(r"D:\groupppro\orig.png"),
                size=(800, 450)
            )
            self.bg_label = CTk.CTkLabel(master=self, text="", image=self.bg_image)
            self.bg_label.place(x=0, y=0)
        except Exception as e:
            print(f"Ошибка при загрузке фонового изображения: {e}")

        self.main_frame = CTk.CTkFrame(master=self, fg_color="transparent", border_width=0)
        self.main_frame.place(relx=0.1, rely=0.2, relwidth=0.6, relheight=0.6)
        self.main_frame.place_forget()

        # Use lambda to defer method calls
        buttons_data = [
            {"text": "Уведомления", "fg_color": "gray", "hover_color": "darkblue", "rely": 0.15, "command": lambda: self.show_notifications()},
            {"text": "Сменить звуки", "fg_color": "gray", "hover_color": "darkgreen", "rely": 0.25, "command": lambda: self.show_sound_presets()},
            {"text": "Мониторинг пк", "fg_color": "gray", "hover_color": "darkred", "rely": 0.35, "command": lambda: self.on_button3_click()},
            {"text": "Кастомизация Windows", "fg_color": "gray", "hover_color": "darkorange", "rely": 0.50, "command": lambda: self.show_windows_customization()},
            {"text": "Побегушки", "fg_color": "gray", "hover_color": "darkviolet", "rely": 0.65, "command": lambda: self.on_button5_click()},
            {"text": "Настройки", "fg_color": "gray", "hover_color": "saddlebrown", "rely": 0.75, "command": lambda: self.on_button6_click()},
        ]

        for button_info in buttons_data:
            button = CTk.CTkButton(
                master=self,
                text=button_info["text"],
                command=button_info["command"],
                fg_color=button_info["fg_color"],
                hover_color=button_info["hover_color"],
                text_color="white",
                font=CTk.CTkFont(size=16, weight="bold")
            )
            button.place(relx=0.86, rely=button_info["rely"], anchor=tk.CENTER)

        self.theme_slider = CTk.CTkSlider(
            master=self,
            from_=0, to=1,
            number_of_steps=1,
            command=self.update_theme,
            width=80,
            height=20,
            button_length=15,
            border_width=2,
        )
        self.theme_slider.set(1)
        self.theme_slider.place(relx=0.8, rely=0.9, anchor=tk.CENTER)

        self.theme_label = CTk.CTkLabel(
            master=self,
            text="Тема",
            font=CTk.CTkFont(size=14, weight="bold"),
        )
        self.theme_label.place(relx=0.9, rely=0.85, anchor=tk.CENTER)

    def update_theme(self, value):
        if value == 0:
            CTk.set_appearance_mode("dark")
        else:
            CTk.set_appearance_mode("light")
        self.update_idletasks()

    def show_notifications(self):
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()

        self.main_frame = CTk.CTkFrame(
            master=self,
            fg_color="transparent",
            border_width=0
        )
        self.main_frame.place(relx=1.0, rely=0.01, relwidth=0.31, relheight=1)

        self.date_entry = CTk.CTkEntry(
            master=self.main_frame,
            placeholder_text="Введите дату и время",
            font=CTk.CTkFont(size=16),
            width=200
        )
        self.date_entry.pack(pady=10)

        self.notification_entry = CTk.CTkEntry(
            master=self.main_frame,
            placeholder_text="Введите текст уведомления",
            font=CTk.CTkFont(size=16),
            width=280
        )
        self.notification_entry.pack(pady=20)

        self.notifications_display = CTk.CTkTextbox(
            master=self.main_frame,
            font=CTk.CTkFont(size=14),
            width=280,
            height=100,
            activate_scrollbars=True
        )
        self.notifications_display.pack(pady=20)
        self.notifications_display.configure(state="disabled")

        self.add_button = CTk.CTkButton(
            master=self.main_frame,
            text="Add",
            command=self.add_notification,
            fg_color="blue",
            hover_color="darkblue",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150
        )
        self.add_button.pack(pady=10)

        self.delete_button = CTk.CTkButton(
            master=self.main_frame,
            text="Удалить",
            command=self.delete_selected_notification,
            fg_color="red",
            hover_color="darkred",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150
        )
        self.delete_button.pack(pady=10)

        self.back_button = CTk.CTkButton(
            master=self.main_frame,
            text="Назад",
            command=self.hide_main_frame,
            fg_color="gray",
            hover_color="darkgray",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150
        )
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        self.animate_frame_in()
        self.update_notifications_display()

    def animate_frame_in(self, current_step=0):
        start_x = 1.0
        end_x = 0.69
        steps = 30
        duration = 300

        if current_step >= steps:
            self.main_frame.place(relx=end_x)
            return

        progress = current_step / steps
        current_x = start_x - (start_x - end_x) * (progress ** 2)

        self.main_frame.place_configure(relx=current_x)
        self.after(int(duration / steps), lambda: self.animate_frame_in(current_step + 1))

    def hide_main_frame(self):
        self.animate_frame_out()

    def animate_frame_out(self, current_step=0):
        start_x = 0.69
        end_x = 1.0
        steps = 30
        duration = 300

        if current_step >= steps:
            self.main_frame.destroy()
            self.main_frame = None
            return

        progress = current_step / steps
        current_x = start_x + (end_x - start_x) * (progress ** 2)

        self.main_frame.place_configure(relx=current_x)
        self.after(int(duration / steps), lambda: self.animate_frame_out(current_step + 1))

    def add_notification(self):
        date_time = self.date_entry.get().strip()
        text = self.notification_entry.get().strip()

        if date_time and text:
            self.notifications_list.append(f"{date_time} - {text}")
            self.update_notifications_display()
            self.date_entry.delete(0, tk.END)
            self.notification_entry.delete(0, tk.END)
        else:
            tkinter.messagebox.showwarning("Предупреждение", "Заполните все поля!")

    def delete_selected_notification(self):
        try:
            selected_line = int(self.notifications_display.index(tk.INSERT).split('.')[0]) - 1
            if 0 <= selected_line < len(self.notifications_list):
                del self.notifications_list[selected_line]
                self.update_notifications_display()
            else:
                tkinter.messagebox.showwarning("Предупреждение", "Выберите уведомление для удаления!")
        except Exception as e:
            tkinter.messagebox.showerror("Ошибка", f"Не удалось удалить уведомление: {e}")

    def update_notifications_display(self):
        self.notifications_display.configure(state="normal")
        self.notifications_display.delete("1.0", tk.END)
        self.notifications_display.insert(tk.END, "\n".join(self.notifications_list))
        self.notifications_display.configure(state="disabled")

    def show_sound_presets(self):
        self.main_frame = CTk.CTkFrame(master=self, fg_color="transparent", border_width=0)
        self.main_frame.place(relx=0.69, rely=0.1, relwidth=0.3, relheight=0.9)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        presets_data = [
            {"text": "Пресет 1", "command": lambda: self.select_preset(1)},
            {"text": "Пресет 2", "command": lambda: self.select_preset(2)},
            {"text": "Пресет 3", "command": lambda: self.select_preset(3)},
            {"text": "Пресет 4", "command": lambda: self.select_preset(4)},
            {"text": "Пресет 5", "command": lambda: self.select_preset(5)},
        ]

        self.keyboard_sound_slider = CTk.CTkSlider(
            master=self.main_frame,
            from_=0, to=1,
            number_of_steps=1,
            command=lambda value: self.update_keyboard_sound(value),
            width=80,
            height=15,
            button_length=15,
            border_width=2
        )
        self.keyboard_sound_slider.set(1)
        self.keyboard_sound_slider.place(relx=0.2, rely=0.6, anchor=tk.CENTER)

        self.keyboard_sound_label = CTk.CTkLabel(
            master=self.main_frame,
            text="Звук с клавиатуры",
            font=CTk.CTkFont(size=12, weight="bold")
        )
        self.keyboard_sound_label.place(relx=0.3, rely=0.55, anchor=tk.CENTER)

        self.mouse_sound_slider = CTk.CTkSlider(
            master=self.main_frame,
            from_=0, to=1,
            number_of_steps=1,
            command=lambda value: self.update_mouse_sound(value),
            width=80,
            height=15,
            button_length=15,
            border_width=2
        )
        self.mouse_sound_slider.set(1)
        self.mouse_sound_slider.place(relx=0.2, rely=0.8, anchor=tk.CENTER)

        self.mouse_sound_label = CTk.CTkLabel(
            master=self.main_frame,
            text="Звук с мышки",
            font=CTk.CTkFont(size=12, weight="bold")
        )
        self.mouse_sound_label.place(relx=0.2, rely=0.75, anchor=tk.CENTER)

        for idx, preset in enumerate(presets_data):
            button = CTk.CTkButton(
                master=self.main_frame,
                text=preset["text"],
                command=preset["command"],
                fg_color="gray",
                hover_color="darkgray",
                text_color="white",
                font=CTk.CTkFont(size=16, weight="bold"),
                width=100
            )
            button.pack(pady=5, side=tk.TOP, anchor=tk.W, padx=(50, 0))

        self.back_button = CTk.CTkButton(
            master=self.main_frame,
            text="Назад",
            command=self.hide_main_frame,
            fg_color="gray",
            hover_color="darkgray",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150
        )
        self.back_button.pack(side=tk.BOTTOM, pady=20)

    def update_keyboard_sound(self, value):
        if value == 0:
            print("Звук с клавиатуры выключен")
        elif value == 1:
            print("Звук с клавиатуры включен")

    def update_mouse_sound(self, value):
        if value == 0:
            print("Звук с мышки выключен")
        elif value == 1:
            print("Звук с мышки включен")

    def select_preset(self, preset_number):
        presets_content = [
            {"keys": "sounds/key_sound.mp3", "mouse": "sounds/key_sound.mp3"},
            {"keys": "sounds/fart_sound.mp3", "mouse": "sounds/fart_sound.mp3"},
            {"keys": "sounds/key_sound.mp3", "mouse": "sounds/key_sound.mp3"},
            {"keys": "sounds/key_sound.mp3", "mouse": "sounds/key_sound.mp3"},
            {"keys": "sounds/key_sound.mp3", "mouse": "sounds/key_sound.mp3"}
        ]
        if self.keyboard_sounds_process is not None and self.keyboard_sounds_process.poll() is None:
            tkinter.messagebox.showwarning("Предупреждение", "Keyboardsounds уже запущен!")
            return

        try:
            self.keyboard_sounds_process = subprocess.Popen(['python', 'KeyboardSounds.py',
                                                             presets_content[preset_number-1]["keys"],
                                                             presets_content[preset_number-1]["mouse"]
                                                             ])
            print(f"WalkingCreature started with PID: {self.keyboard_sounds_process.pid}")
        except FileNotFoundError:
            print("Файл KeyboardSounds.py не найден. Убедитесь, что он находится в той же директории.")
            tkinter.messagebox.showerror("Ошибка", "KeyboardSounds.py не найден!")
        except Exception as e:
            print(f"Ошибка при запуске KeyboardSounds.py: {e}")
            tkinter.messagebox.showerror("Ошибка", f"Не удалось запустить KeyboardSounds: {e}")

    def show_windows_customization(self):
        self.main_frame = CTk.CTkFrame(master=self, fg_color="transparent", border_width=0)
        self.main_frame.place(relx=0.69, rely=0.1, relwidth=0.34, relheight=0.9)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        customization_options = [
            {"text": "леха", "command": lambda: self.select_customization_option(1)},
            {"text": "85", "command": lambda: self.select_customization_option(2)},
            {"text": "Пичугин", "command": lambda: self.select_customization_option(3)},
            {"text": "Пенис", "command": lambda: self.select_customization_option(4)},
            {"text": "Джонклер", "command": lambda: self.select_customization_option(5)},
        ]

        for idx, option in enumerate(customization_options):
            button = CTk.CTkButton(
                master=self.main_frame,
                text=option["text"],
                command=option["command"],
                fg_color="gray",
                hover_color="darkgray",
                text_color="white",
                font=CTk.CTkFont(size=16, weight="bold"),
                width=150
            )
            button.pack(pady=5)

        self.back_button = CTk.CTkButton(
            master=self.main_frame,
            text="Назад",
            command=self.hide_main_frame,
            fg_color="gray",
            hover_color="darkgray",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150
        )
        self.back_button.pack(side=tk.BOTTOM, pady=20)

    def select_customization_option(self, option_number):
        print(f"Выбрана опция кастомизации: {option_number}")

    def on_button3_click(self):
        self.hide_main_frame()

        self.monitoring_frame = CTk.CTkFrame(master=self, fg_color="transparent", border_width=0)
        self.monitoring_frame.place(relx=0.69, rely=0.01, relwidth=0.31, relheight=1)

        for widget in self.monitoring_frame.winfo_children():
            widget.destroy()

        self.title_label = CTk.CTkLabel(
            master=self.monitoring_frame,
            text="Мониторинг ПК",
            font=CTk.CTkFont(size=18, weight="bold"),
        )
        self.title_label.pack(pady=20)

        self.info_textbox = CTk.CTkTextbox(
            master=self.monitoring_frame,
            width=300,
            height=200,
            font=CTk.CTkFont(size=14),
            activate_scrollbars=True
        )
        self.info_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        self.info_textbox.insert("0.0", "Информация о системе будет отображаться здесь...\n\n")

        self.update_button = CTk.CTkButton(
            master=self.monitoring_frame,
            text="Обновить",
            command=self.update_system_info,
            fg_color="blue",
            hover_color="darkblue",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150,
        )
        self.update_button.pack(pady=10)

        self.back_button = CTk.CTkButton(
            master=self.monitoring_frame,
            text="Назад",
            command=self.hide_monitoring_frame,
            fg_color="gray",
            hover_color="darkgray",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150,
        )
        self.back_button.pack(side=tk.BOTTOM, pady=20)

    def update_system_info(self):
        system_info = (
            "Системная информация:\n"
            "---------------------\n"
            "Загрузка CPU: 45%\n"
            "Использование памяти: 60%\n"
            "Температура CPU: 55°C\n"
            "Диск C: 70% занят\n"
            "---------------------\n"
            "Эти данные взяты из другого кода."
        )
        self.info_textbox.delete("0.0", "end")
        self.info_textbox.insert("0.0", system_info)
        print("Информация о системе обновлена")

    def hide_monitoring_frame(self):
        self.monitoring_frame.place_forget()

    def on_button5_click(self):
        self.main_frame = CTk.CTkFrame(master=self, fg_color="transparent", border_width=0)
        self.main_frame.place(relx=0.69, rely=0.01, relwidth=0.31, relheight=1)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.title_label = CTk.CTkLabel(
            master=self.main_frame,
            text="Выберите режим скорости",
            font=CTk.CTkFont(size=16, weight="bold"),
        )
        self.title_label.pack(pady=20)

        self.speed_slider = CTk.CTkSlider(
            master=self.main_frame,
            from_=1, to=5,
            number_of_steps=4,
            command=self.update_speed_mode,
            width=200,
            height=20,
            button_length=15,
            border_width=2,
        )
        self.speed_slider.set(1)
        self.speed_slider.pack(pady=20)

        self.speed_label = CTk.CTkLabel(
            master=self.main_frame,
            text=f"Текущий режим: {int(self.speed_slider.get())}",
            font=CTk.CTkFont(size=14, weight="bold"),
        )
        self.speed_label.pack(pady=10)

        self.confirm_button = CTk.CTkButton(
            master=self.main_frame,
            text="Подтвердить",
            command=self.confirm_speed_mode,
            fg_color="green",
            hover_color="darkgreen",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150,
        )
        self.confirm_button.pack(pady=10)

        self.off_button = CTk.CTkButton(
            master=self.main_frame,
            text="Выключить",
            command=self.turn_off_system,
            fg_color="red",
            hover_color="darkred",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150,
        )
        self.off_button.pack(pady=10)

        self.back_button = CTk.CTkButton(
            master=self.main_frame,
            text="Назад",
            command=self.hide_main_frame,
            fg_color="gray",
            hover_color="darkgray",
            text_color="white",
            font=CTk.CTkFont(size=16, weight="bold"),
            width=150,
        )
        self.back_button.pack(side=tk.BOTTOM, pady=20)

    def update_speed_mode(self, value):
        speed_mode = int(value)
        self.speed_label.configure(text=f"Текущий режим: {speed_mode}")
        print(f"Выбранный режим скорости: {speed_mode}")

    def confirm_speed_mode(self):
        speed_mode = int(self.speed_slider.get())
        print(f"Подтверждённый режим скорости: {speed_mode}")

        if self.walking_creature_process is not None and self.walking_creature_process.poll() is None:
            tkinter.messagebox.showwarning("Предупреждение", "WalkingCreature уже запущен!")
            return

        try:
            self.walking_creature_process = subprocess.Popen(['python', 'WalkingCreature.py', str(speed_mode*100)])
            print(f"WalkingCreature started with PID: {self.walking_creature_process.pid}")
        except FileNotFoundError:
            print("Файл WalkingCreature.py не найден. Убедитесь, что он находится в той же директории.")
            tkinter.messagebox.showerror("Ошибка", "WalkingCreature.py не найден!")
        except Exception as e:
            print(f"Ошибка при запуске WalkingCreature.py: {e}")
            tkinter.messagebox.showerror("Ошибка", f"Не удалось запустить WalkingCreature: {e}")

    def turn_off_system(self):
        if self.walking_creature_process is not None and self.walking_creature_process.poll() is None:
            self.walking_creature_process.terminate()
            self.walking_creature_process.wait()
            self.walking_creature_process = None
            print("WalkingCreature выключен")
        else:
            print("WalkingCreature не запущен")

    def hide_main_frame(self):
        self.main_frame.place_forget()

    def on_button6_click(self):
        self.hide_main_frame()
        tkinter.messagebox.showinfo("Информация", "Вы нажали Настройки!")

    def destroy(self):
        if self.walking_creature_process is not None and self.walking_creature_process.poll() is None:
            self.walking_creature_process.terminate()
        super().destroy()

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.mainloop()