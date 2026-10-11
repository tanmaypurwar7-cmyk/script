
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
        raise FileNotFoundError(
            f"Missing message file: {message_path}"
        )

    return message_path.read_text(encoding="utf-8-sig").strip()


def load_numbers(numbers_path: Path) -> list[str]:
    if not numbers_path.exists():
        raise FileNotFoundError(
            f"Missing numbers file: {numbers_path}"
        )

    raw_data = numbers_path.read_bytes()

    # Support UTF-8 and UTF-16 files.
    if raw_data.startswith((b"\xff\xfe", b"\xfe\xff")):
        content = raw_data.decode("utf-16")
    else:
        content = raw_data.decode("utf-8-sig")

    numbers = []

    for line in content.splitlines():
        number = clean_number(line.strip())

        if number:
            numbers.append(number)

    # Remove duplicate numbers while preserving order.
    return list(dict.fromkeys(numbers))


def clean_number(number: str) -> str:
    # Keep digits only, allowing numbers with +, spaces,
    # parentheses, and hyphens.
    number = number.strip()

    if not number:
        return ""

    number = re.sub(r"\D", "", number)

    # Ignore empty entries and entries without digits.
    return number


def open_chat(number: str, message: str) -> None:
    url = (
        f"https://web.whatsapp.com/send"
        f"?phone={number}"
        f"&text={quote(message)}"
    )

    # Open using the system's default browser.
    webbrowser.open(url, new=2)


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    numbers_path = base_dir / NUMBERS_FILE
    image_path = base_dir / IMAGE_FILE

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing poster image: {image_path}"
        )

    message = load_message(base_dir)
    numbers = load_numbers(numbers_path)

    if not numbers:
        print("No valid phone numbers found in numbers.txt.")
        return

    print(f"Loaded {len(numbers)} phone numbers.")
    print()
    print("Keep this script running.")
    print("Press Enter anywhere to advance the workflow.")
    print("Press Ctrl+C in the terminal to stop.")
    print()
    print("Sequence: OPEN CHAT -> ATTACH POSTER AND SEND MANUALLY")
    print("The first Enter opens the first chat.")
    print("Attach the poster and send the message manually.")
    print("Press Enter again when you're ready for the next chat.")
    print()

    index = 0
    lock = threading.Lock()

    def on_press(key):
        nonlocal index

        if key != keyboard.Key.enter:
            return

        with lock:
            if index >= len(numbers):
                return False

            number = numbers[index]
            index += 1

            try:
                open_chat(number, message)
                print(
                    f"\nOpened chat {index}/{len(numbers)} "
                    f"for number {number}."
                )
                print("Wait for WhatsApp Web to load.")
                print("Attach the poster and send the message manually.")

                if index < len(numbers):
                    print("Press Enter again when you're ready for the next chat.")
                else:
                    print("\nAll contacts opened.")
                    return False  # Stop keyboard listener

            except Exception as error:
                print(f"Could not open chat for {number}: {error}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        listener.join()
    except KeyboardInterrupt:
        print("\nScript stopped.")
        listener.stop()


    try:
        listener.join()
    except KeyboardInterrupt:
        print("\nScript stopped.")
        listener.stop()


if __name__ == "__main__":
    main()
