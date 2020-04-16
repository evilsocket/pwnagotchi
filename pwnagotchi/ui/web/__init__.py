import os
from threading import Lock

frame_path = '/var/tmp/pwnagotchi/pwnagotchi.png'
frame_format = 'PNG'
frame_ctype = 'image/png'
frame_lock = Lock()


def update_frame(img):
    global frame_lock, frame_path, frame_format
    if not os.path.exists(os.path.dirname(frame_path)):
        os.makedirs(os.path.dirname(frame_path))
    with frame_lock:
        img.save(frame_path, format=frame_format)
