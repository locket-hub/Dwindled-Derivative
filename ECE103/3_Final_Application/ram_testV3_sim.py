# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "opencv-python",
#     "numpy",
# ]
# ///

import cv2
import time
import os
import numpy as np

"""
SIMULATION NOTES
_______________________________
This is a keyboard-only stand-in for ram_testV3.py, for testing the
fade/loop logic on a machine with no Pi GPIO, no break-beam sensor,
and no camera attached.

  - Enter still starts a cycle (same as the real app).
  - Each break-beam event is simulated by pressing SPACE while the
    "Fade Preview" window is focused (a real beam-break has a
    break-then-restore pair; here one SPACE press just advances to
    the next fade step, since a keyboard has no natural "restore").
  - The camera capture is replaced with a generated placeholder image
    so there's something to fade.
"""

filename = "pic.png"
sub_folder = "PhotoInput"
current_directory = os.getcwd()
images_tosubpath = os.path.join(current_directory, sub_folder)
images_path = os.path.join(images_tosubpath, filename)

os.makedirs(images_tosubpath, exist_ok=True)


"""
BREAK BEAM SETUP (simulated via keyboard)
_______________________________________________________
"""

def wait_for_beam_break_nonblocking():
    print("Waiting for beam break... (press SPACE in the Fade Preview window)")

    while True:
        key = cv2.waitKey(30) & 0xFF
        if key == 32:  # spacebar
            break
        if key == ord('q'):
            raise KeyboardInterrupt

    print("Beam broken! (simulated)")


"""
PHOTO CAPTURE (simulated - no camera required)
_______________________________________________
"""

def take_picture():
    print("Warmup (simulated)")
    time.sleep(0.5)

    # Generate a placeholder frame in place of a real camera capture.
    height, width = 1920, 1080
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    gradient = np.linspace(0, 255, width, dtype=np.uint8)
    frame[:, :, 0] = gradient  # horizontal gradient so fading is visible
    frame[:, :, 1] = 128
    frame[:, :, 2] = np.linspace(255, 0, width, dtype=np.uint8)

    cv2.putText(frame, "SIMULATED PHOTO", (60, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

    cv2.imwrite(images_path, frame)
    print("Picture saved:", images_path)

    return frame


"""
FADE IN RAM
_______________________
"""

# cv2.namedWindow("Fade Preview", cv2.WINDOW_NORMAL)
# cv2.setWindowProperty("Fade Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def fade_to_black_cv(img, level):

    faded = cv2.convertScaleAbs(img, alpha=level, beta=0)

    cv2.imshow("Fade Preview", faded)
    cv2.waitKey(1)


def increment_fade(img):
    fade_steps = [0.7, 0.4, 0.2, 0.0]

    cv2.namedWindow("Fade Preview", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Fade Preview", 540, 960)

    print("First Display Test")
    fade_to_black_cv(img, 1.0)
    time.sleep(0.5)

    for level in fade_steps:
        wait_for_beam_break_nonblocking()
        print("Applying fade level:", level)
        fade_to_black_cv(img, level)


"""
PROGRAM START
___________________________

"""


try:
    while True:
        userInput = input("Please click Enter (or type 'q' to quit): ")

        if userInput.lower() == "q":
            break

        if userInput == "":
            img = take_picture()

            if img is not None:
                increment_fade(img)
            else:
                print("No image captured.")
        else:
            print("You didn't press Enter.")

finally:
    cv2.destroyAllWindows()
