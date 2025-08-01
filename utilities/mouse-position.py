# utilities/mouse-position.py
# This script captures the mouse click position and prints it to the console.
# This can be used for configuration purposes or debugging. The script uses the `pynput` library.
# Ensure you have installed the python packages in utilities/utility-requirements.txt

from pynput import mouse


def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at: ({x}, {y})")
        return False


while True:
    with mouse.Listener(on_click=on_click) as listener:
        print("Click anywhere to capture coordinates...")
        listener.join()
