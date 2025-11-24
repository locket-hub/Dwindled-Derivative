import subprocess
import time
from PIL import Image, ImageEnhance
import os
import RPi.GPIO as GPIO

"""

Photo Directories

"""

# InputPath
filename = "pic.png"
sub_folder = "PhotoInput"
current_directory = os.getcwd()
images_tosubpath = os.path.join(current_directory, sub_folder)
images_path = os.path.join(images_tosubpath, filename)

# OutputPath
output_sub_folder = "PhotoOutput"
output_current_directory = os.getcwd()
output_images_tosubpath = os.path.join(output_current_directory, output_sub_folder)

# Ensure folders exist
os.makedirs(images_tosubpath, exist_ok=True)
os.makedirs(output_images_tosubpath, exist_ok=True)

"""

Break Beam Sensor Setup

"""

BEAM_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_for_beam_break():
    """
    Block until the beam is broken (FALLING edge),
    then block until it is unbroken again (RISING edge),
    so each physical pass only advances one step.
    """
    print("Waiting for beam break to take photo...")
    GPIO.wait_for_edge(BEAM_PIN, GPIO.FALLING)
    print("Beam broken")

    print("Waiting for beam to be unbroken...")
    GPIO.wait_for_edge(BEAM_PIN, GPIO.RISING)
    print("Beam unbroken, ready for next step.")

"""

Image/Fading Function

"""

def take_picture():
    command = [
        "fswebcam",
        "-d", "/dev/video0",  # With no other webcam devices, this is default
        "-r", "1920x1080",
        "-S", "60",  # 60 Frames Skipped
        images_path
    ]
    subprocess.call(command)
    print("Pic Captured:", images_path)


def fade_to_black(level, index):
    img = Image.open(images_path).convert("RGB")
    enhancer = ImageEnhance.Brightness(img)
    darker = enhancer.enhance(level)

    fade_filename = f"fade_{index}.png"
    fade_path = os.path.join(output_images_tosubpath, fade_filename)
    darker.save(fade_path)

    # If you really want to preview, only do it once or for debugging
    # to_preview = Image.open(fade_path)
    # to_preview.show()

    print(f"Saved brightness level {level} -> {fade_path}")


def increment_fade():
    # From full brightness -> black
    fade_steps = [1.0, 0.7, 0.4, 0.2, 0.0]  # For five pages

    for idx, level in enumerate(fade_steps):
        # Wait for a beam break *before* each new frame
        wait_for_beam_break()
        fade_to_black(level, idx)


"""

User Input

"""

try:
    userInput = input("Please click Enter: ")

    if userInput == "":
        take_picture()
        increment_fade()
    else:
        print("You didn't press Enter.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
