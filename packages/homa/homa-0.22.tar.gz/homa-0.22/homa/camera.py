import cv2
from .classes.Repository import Repository


def camera(delay=10):
    capture = cv2.VideoCapture(0)

    pressed_key = None

    frame_number = 0

    while pressed_key != ord("q"):
        frame_number += 1
        _, frame = capture.read()

        Repository.images["camera"] = frame

        yield frame_number
        pressed_key = cv2.waitKey(delay)

    capture.release()
