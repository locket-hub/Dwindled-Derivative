import cv2
import time
import os
import numpy as np


"""
***This will be for having live-feed before ultra-sensor is triggered,
    picture is taken, compressed, and shown on a timer***

import subprocess

try:
    print("Launching camera preview... Press Ctrl+C in this terminal to exit.")
    # Run the shell command. This blocks Python execution until the preview window is closed.
    subprocess.run(["rpicam-hello", "-t", "0"], check=True)
except KeyboardInterrupt:
    print("\nPreview stopped by user.")
except subprocess.CalledProcessError as e:
    print(f"Error running rpicam-hello: {e}")
"""



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
MOCK BREAK BEAM
_______________________________________________________
"""


def wait_for_beam_break_nonblocking():
    print("Waiting for beam break...")

    time.sleep(4)

    print("Beam unbroken!")


"""
PHOTO CAPTURE
_______________________________________________
"""

def take_picture():
    # Chooses first camera, keep this mind
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cam.isOpened():
        print("Camera not found")
        return None

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)

    print("Warmup")
    warmup = time.time() + 3

    while time.time() < warmup:
        cam.read()

    ret, frame = cam.read()
    cam.release

    if not ret or frame is None:
        print("Camera capture error")
        return None

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
    cv2.waitKey(100)
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
    print("Mock GPIO cleaned up.")
    cv2.destroyAllWindows()
