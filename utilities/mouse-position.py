from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at: ({x}, {y})")
        return False

while True:
    with mouse.Listener(on_click=on_click) as listener:
        print("Click anywhere to capture coordinates...")
        listener.join()
