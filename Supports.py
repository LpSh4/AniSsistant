import os, json, threading

def turnint(a): #Turning user input into int if possibel
    try:
        a = int(a)
    except ValueError:
        pass
    return a

def resource_path(relative_path):   #Get absolute path to the resource
    return os.path.join(os.path.abspath("."), relative_path)

def open_json(path):    #Reading JSON variables
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def play_sound(sound):  #Play sound in separate thread
    threading.Thread(target=sound.play, daemon=True).start()