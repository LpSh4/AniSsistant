import win32gui
import win32con
import win32ui
import win32api
import time
import sys
from PIL import Image
import os
import signal

# Global variable to store original icon
original_icon = None
hwnd = None


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def set_custom_icon(window_title, icon_path):
    global original_icon, hwnd

    # Find the window by title
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Could not find window with title: {window_title}")
        return False

    # Get the original icon to restore later
    original_icon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_SMALL2, 0)
    if not original_icon:
        original_icon = win32gui.GetClassLong(hwnd, win32con.GCL_HICONSM)

    # Load and convert the PNG to Windows icon format
    try:
        # Open the PNG with PIL and resize to 128x128 if needed
        img = Image.open(icon_path)
        if img.size != (128, 128):
            img = img.resize((128, 128), Image.Resampling.LANCZOS)

        # Convert to ICO format in memory
        icon = img.tobytes()
        hicon = win32gui.CreateIconFromResource(icon, len(icon), True, 0x00030000)

        # Set the new icon
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL2, hicon)
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

        return True
    except Exception as e:
        print(f"Error setting icon: {e}")
        return False


def restore_original_icon():
    global original_icon, hwnd
    if hwnd and original_icon:
        # Restore the original icon
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL2, original_icon)
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, original_icon)
        print("Original icon restored")


def signal_handler(sig, frame):
    """Handle Ctrl+C to restore icon and exit"""
    restore_original_icon()
    sys.exit(0)


def main():
    # Configuration
    WINDOW_TITLE = "Your Application Title"  # Change this to match your app's window title
    CUSTOM_ICON_PATH = resource_path("custom_icon.png")  # Path to your 128x128 PNG

    # Verify icon exists
    if not os.path.exists(CUSTOM_ICON_PATH):
        print(f"Icon file not found at: {CUSTOM_ICON_PATH}")
        return

    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # Set the custom icon
    if set_custom_icon(WINDOW_TITLE, CUSTOM_ICON_PATH):
        print("Custom icon set successfully")
        print("Press Ctrl+C to exit and restore original icon")

        # Keep script running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            restore_original_icon()
    else:
        print("Failed to set custom icon")


if __name__ == "__main__":
    # Install required packages if not present
    try:
        import pywin32
    except ImportError:
        print("Installing required package: pywin32")
        os.system("pip install pywin32")

    try:
        import Pillow
    except ImportError:
        print("Installing required package: Pillow")
        os.system("pip install Pillow")

    main()