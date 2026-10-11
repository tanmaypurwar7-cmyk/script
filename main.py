import re
import threading
import webbrowser
from pathlib import Path
from urllib.parse import quote
from pynput import keyboard

NUMBERS_FILE = "numbers.txt"
IMAGE_FILE = "tantrafiesta_poster.png"
MESSAGE_FILE = "message.txt"


def load_message(base_dir: Path) -> str:
    message_path = base_dir / MESSAGE_FILE

    if not message_path.exists():
        raise FileNotFoundError(f"Missing message file: {message_path}")

    return message_path.read_text(encoding="utf-8").strip()


def clean_number(number):
    return re.sub(r"\D", "", number)


def main():
    base_dir = Path(__file__).resolve().parent
    numbers_path = base_dir / NUMBERS_FILE
    image_path = base_dir / IMAGE_FILE
    message_path = base_dir / MESSAGE_FILE

    if not numbers_path.exists():
        print(f"Missing file: {numbers_path}")
        return

    if not image_path.exists():
        print(f"Missing poster: {image_path}")
        return

    if not message_path.exists():
        print(f"Missing message file: {message_path}")
        return

    try:
        message = load_message(base_dir)
    except FileNotFoundError as error:
        print(error)
        return

    with open(numbers_path, encoding="utf-8") as file:
        numbers = list(dict.fromkeys(
            clean_number(line.strip())
            for line in file
            if clean_number(line.strip())
        ))

    if not numbers:
        print("No phone numbers found in numbers.txt")
        return

    state = {
        "index": 0,
        "action": "open",
        "busy": False,
        "stop": False,
    }

    lock = threading.Lock()

    print(f"Loaded {len(numbers)} phone numbers.")
    print("\nKeep this script running.")
    print("Press Enter anywhere to advance the workflow.")
    print("Press Ctrl+C in the terminal to stop.")
    print("\nSequence: OPEN CHAT -> ATTACH POSTER AND SEND MANUALLY")
    print("The first Enter opens the first chat.")

    def open_chat(index):
        number = numbers[index]

        url = (
            "https://web.whatsapp.com/send"
            f"?phone={number}&text={quote(message)}"
        )

        try:
            opened = webbrowser.open(url, new=2)

            if not opened:
                print("\nCould not open the default browser.")
                return False

            print(
                f"\nOpened chat {index + 1}/{len(numbers)} "
                f"for number {number}."
            )
            print("Wait for WhatsApp Web to load.")
            print("Attach the poster and send the message manually.")
            print("Press Enter again when you're ready for the next chat.")

            return True

        except Exception as error:
            print(f"\nCould not open the chat: {error}")
            return False

    def on_press(key):
        if key != keyboard.Key.enter:
            return

        with lock:
            if state["busy"] or state["stop"]:
                return

            state["busy"] = True

        try:
            if state["action"] == "open":
                if open_chat(state["index"]):
                    state["action"] = "next"

            else:
                next_index = state["index"] + 1

                if next_index >= len(numbers):
                    print("\nAll contacts processed.")
                    state["stop"] = True
                    return False

                if open_chat(next_index):
                    state["index"] = next_index
                    state["action"] = "next"

        finally:
            with lock:
                state["busy"] = False

    with keyboard.Listener(on_press=on_press) as listener:
        try:
            while not state["stop"]:
                listener.join(timeout=0.5)
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            listener.stop()


if __name__ == "__main__":
    main()