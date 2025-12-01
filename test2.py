
import cv2
import time
import os
import RPi.GPIO as GPIO
import numpy as np

"""
=========================================================
1. DIRECTORY SETUP
=========================================================
Only save ONE picture: the original. Fades are done in
memory now, not written to disk.
=========================================================
"""

filename = "pic.png"
sub_folder = "PhotoInput"
current_directory = os.getcwd()
images_tosubpath = os.path.join(current_directory, sub_folder)
images_path = os.path.join(images_tosubpath, filename)

os.makedirs(images_tosubpath, exist_ok=True)


"""
=========================================================
2. BREAK BEAM SETUP (Non-blocking version)
=========================================================
This keeps OpenCV responsive by avoiding wait_for_edge(),
which freezes the GUI. We poll instead.
=========================================================
"""

BEAM_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_for_beam_break_nonblocking():
    print("Waiting for beam break...")

    # FALLING: beam becomes broken
    while GPIO.input(BEAM_PIN) == 1:
        cv2.waitKey(1)
        time.sleep(0.01)

    print("Beam broken!")

    # RISING: beam restored
    print("Waiting for beam restore...")
    while GPIO.input(BEAM_PIN) == 0:
        cv2.waitKey(1)
        time.sleep(0.01)

    print("Beam unbroken!")


"""
=========================================================
