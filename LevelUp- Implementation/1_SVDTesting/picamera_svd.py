import cv2
import time
import os
import RPi.GPIO as GPIO
import numpy as np
from picamera2 import Picamera2
from PIL import Image
import matplotlib.pyplot as plt

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
BREAK BEAM SETUP
_______________________________________________________
"""

BEAM_PIN = 17

GPIO.setmode(GPIO.BCM)
# To avoid using a physical on bread board resistor
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_for_beam_break_nonblocking():
    print("Waiting for beam break...")

    while GPIO.input(BEAM_PIN) == 1:
        cv2.waitKey(1)
        time.sleep(0.01)

    print("Beam broken!")

    print("Waiting for beam restore...")
    while GPIO.input(BEAM_PIN) == 0:
        cv2.waitKey(1)
        time.sleep(0.01)

    print("Beam unbroken!")


"""
PHOTO CAPTURE
_______________________________________________
"""

def take_picture():
    cam = Picamera2()

    # Inverted for portrait
    config = cam.create_still_configuration(
        main={"size": (1920, 1080), "format": "RGB888"}
    )
    cam.configure(config)
    cam.start()

    print("Warmup")
    time.sleep(2)

    frame = cam.capture_array()
    cam.stop()

    # picamera2 gives RGB, cv2 expects BGR — swap channels
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Your rotation stays the same
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite(images_path, frame)
    print("Picture saved:", images_path)

    return frame



"""
FADE IN RAM
_______________________
"""


def increment_fade(img):
    # 5 phases, 4 shifts matching number of pages

    # Original started at 80
    k_steps = [60, 35, 10]

    print("Pre-computing SVD steps...")
    frames = [svd_compress_frame(img, k) for k in k_steps]
    print("Done.")

    cv2.namedWindow("Fade Preview", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Fade Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Fade Preview", gray_full)
    cv2.waitKey(1)
    time.sleep(0.5)

    for k, frame in zip(k_steps, frames):
        wait_for_beam_break_nonblocking()
        print(f"Showing rank k={k}")
        cv2.imshow("Fade Preview", frame)
        cv2.waitKey(1)

    wait_for_beam_break_nonblocking()
    print("Going black")
    cv2.imshow("Fade Preview", np.zeros_like(gray_full))
    cv2.waitKey(1)

"""
SVD Compression
___________________________
"""

def svd_compress_frame(img, k, scale=0.25):
    h, w = img.shape[:2]
    
    # Convert to grayscale and downsample
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (int(w * scale), int(h * scale)))
    
    # SVD on small grayscale image
    U, S, Vt = np.linalg.svd(small.astype(float), full_matrices=False)
    reconstructed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    compressed_small = np.clip(reconstructed, 0, 255).astype(np.uint8)
    
    # Scale back up to original resolution
    return cv2.resize(compressed_small, (w, h))

def _compress_channel(channel, k):
    channel = channel.astype(float)
    U, S, Vt = np.linalg.svd(channel, full_matrices=False)
    reconstructed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    return np.clip(reconstructed, 0, 255)


"""
PROGRAM START
___________________________

"""


try:
    userInput = input("Please click Enter: ")

    if userInput == "":
        img = take_picture()

        if img is not None:
            increment_fade(img)
        else:
            print("No image captured.")
    else:
        print("You didn't press Enter.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
    cv2.destroyAllWindows()

    # Needs to loop
