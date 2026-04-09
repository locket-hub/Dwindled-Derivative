import tkinter as tk
from tkinter import ttk
import cv2
import time
import os
import RPi.GPIO as GPIO
import numpy as np
from gpiozero import DistanceSensor

"""
DIRECTORY
_______________________________
"""

filename = "pic.png"
sub_folder = "PhotoInput"
current_directory = os.getcwd()
images_tosubpath = os.path.join(current_directory, sub_folder)
images_path = os.path.join(images_tosubpath, filename)

os.makedirs(images_tosubpath, exist_ok=True)

"""
ULTRA-SONIC SENSOR & BEAM SETUP
_______________________________
"""

dist_sensor = DistanceSensor(echo=23, trigger=24, max_distance=4)

BEAM_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_for_beam_break_nonblocking():
    print("Waiting for beam break...")
    while GPIO.input(BEAM_PIN) == 1:
        cv2.waitKey(1)
        time.sleep(0.01)
    print("Beam broken!")
    while GPIO.input(BEAM_PIN) == 0:
        cv2.waitKey(1)
        time.sleep(0.01)
    print("Beam unbroken!")

"""
PHOTO CAPTURE
____________________________
"""

def take_picture():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)

    print("Warmup...")
    time.sleep(2)

    for _ in range(5):
        cap.read()

    time.sleep(3)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("ERROR: Could not capture image.")
        return None

    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite(images_path, frame)
    print("Picture saved:", images_path)
    return frame

"""
FADE
____________________________
"""

def fade_to_black_cv(img, level):
    faded = cv2.convertScaleAbs(img, alpha=level, beta=0)
    cv2.imshow("Fade Preview", faded)
    cv2.waitKey(1)

def increment_fade(img):
    fade_steps = [0.7, 0.4, 0.2, 0.0]

    cv2.namedWindow("Fade Preview", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Fade Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    fade_to_black_cv(img, 1.0)
    time.sleep(0.5)

    for level in fade_steps:
        wait_for_beam_break_nonblocking()
        print("Applying fade level:", level)
        fade_to_black_cv(img, level)

"""
User Interface
____________________________
"""

def set_status(text):
    status_label.config(text=text)
    root.update_idletasks()

def set_buttons(enabled):
    state = "normal" if enabled else "disabled"
    camera_button.config(state=state)
    sensor_button.config(state=state)
    dropbox_button.config(state=state)

# Camera Booth Functionality

def start_camera_booth():
    set_buttons(False)
    booth_running.set(True)
    root.bind("<Return>", lambda e: booth_loop())
    root.bind("<q>", lambda e: stop_camera_booth())
    root.bind("<Escape>", lambda e: stop_camera_booth())
    booth_loop()

def booth_loop():
    if not booth_running.get():
        return

    set_status("Getting ready...")
    img = take_picture()

    if img is not None:
        set_status("Photo taken! Press Enter to go again, Q/Esc to stop.")
        increment_fade(img)
        cv2.destroyAllWindows()
    else:
        set_status("Camera error.")
        stop_camera_booth()

def stop_camera_booth():
    booth_running.set(False)
    root.unbind("<Return>")
    root.unbind("<q>")
    root.unbind("<Escape>")
    set_buttons(True)
    set_status("Choose an option.")

# Sensor-Triggered Camera Booth Functionality

def start_sensor_booth():
    set_buttons(False)
    set_status("Waiting for someone...")
    poll_distance()

def poll_distance():
    distance = dist_sensor.distance * 100
    print("Distance: %.1f cm" % distance)

    if distance <= 30:
        set_status("Someone detected! Taking photo...")
        root.after(100, run_sensor_photo_sequence)
    else:
        set_status("Waiting for someone... (%.1f cm)" % distance)
        root.after(1000, poll_distance)

def run_sensor_photo_sequence():
    img = take_picture()

    if img is not None:
        set_status("Photo taken! Processing...")
        increment_fade(img)
        cv2.destroyAllWindows()
        set_status("Done! Choose an option.")
    else:
        set_status("Camera error. Try again.")

    set_buttons(True)

# Dropbox Functionality

def start_dropbox():
    set_status("Under construction!")

"""
PROGRAM START
____________________________
"""

root = tk.Tk()
root.title("Photo Booth")
root.geometry("400x220")

booth_running = tk.BooleanVar(value=False)

camera_button = ttk.Button(root, text="Camera Booth", command=start_camera_booth)
camera_button.pack(pady=5)

sensor_button = ttk.Button(root, text="Sensor-Triggered Booth", command=start_sensor_booth)
sensor_button.pack(pady=5)

dropbox_button = ttk.Button(root, text="Upload A Photo", command=start_dropbox)
dropbox_button.pack(pady=5)

status_label = ttk.Label(root, text="Dwindled Book")
status_label.pack(pady=15)

try:
    root.mainloop()
finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
    print("Cleaned up.")