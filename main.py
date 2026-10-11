import re
import subprocess
import threading
from pathlib import Path
from urllib.parse import quote
from pynput import keyboard

NUMBERS_FILE = "numbers.txt"
IMAGE_FILE = "tantrafiesta_poster.png"

message = (
    "\U0001F680 Brace Yourselves for TANTRAFIESTA '26!\n"
    "Themed on\n"
    "ANANTA: SURPASSING THE POSSIBLE\n\n"
    "\U0001F4C5 Mark your calendars for 25 & 26 October 2026!\n\n"
    "The 2026 edition of TantraFiesta, the Grand Technical Fest "
    "of IIIT Nagpur, invites you to think beyond limits, "
    "challenge convention, and build what comes next.\n\n"
    "With a \u20B97,00,000+ prize pool, get ready for two days "
    "of fierce competition, bold ideas, and boundless possibilities.\n\n"
    "\U0001F4BB Premier Hackathons & Coding Duels\n"
    "\U0001F916 Robotics Battles & Autonomous Challenges\n"
    "\U0001F3AE Competitive Gaming & Game Development\n"
    "\U0001F9E0 AI & Emerging Technology Challenges\n"
    "\U0001F3A4 Tech Talks & Hands-on Workshops\n"
    "\U0001F4CA Case Studies, Finance & Startup Competitions\n"
    "\U0001F510 Cybersecurity & Capture the Flag\n"
    "\U0001F3A8 Design & Creative Engineering\n\n"
    "...and a universe of surprises waiting to unfold!\n\n"
    "\U0001F517 Unstop: https://tinyurl.com/cvjxvtcr\n"
    "\U0001F4D6 Event Brochure: https://tinyurl.com/488jk92k\n"
    "\U0001F310 TF 2026 Website: https://www.tantrafiesta.in/"
)

def clean_number(number):
    return re.sub(r"\D", "", number)

def main():
    base_dir = Path(__file__).resolve().parent
    numbers_path = base_dir / NUMBERS_FILE
    image_path = base_dir / IMAGE_FILE

    if not numbers_path.exists():
        print(f"Missing file: {numbers_path}")
        return

    if not image_path.exists():
        print(f"Missing poster: {image_path}")
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
    print("Ctrl+C in Terminal stops the script.")
    print("\nSequence: OPEN CHAT -> PREPARE/SEND MANUALLY -> NEXT CHAT")
    print("The first Enter opens the first chat.")

    def on_press(key):
        if key != keyboard.Key.enter:
            return

        with lock:
            if state["busy"] or state["stop"]:
                return
            state["busy"] = True

        try:
            index = state["index"]

            if state["action"] == "open":
                number = numbers[index]
                url = (
                    "https://web.whatsapp.com/send"
                    f"?phone={number}&text={quote(message)}"
                )

                subprocess.run(
                    ["open", "-a", "Brave Browser", url],
                    check=True
                )

                print(
                    f"\nOpened chat {index + 1}/{len(numbers)} "
                    f"for number {number}."
                )
                print("Wait for WhatsApp Web to load.")
                print("Attach the poster and send the message manually.")
                print("Press Enter again when you're ready for the next chat.")

                state["action"] = "next"

            else:
                state["index"] += 1

                if state["index"] >= len(numbers):
                    print("\nAll contacts processed.")
                    state["stop"] = True
                    return False

                state["action"] = "open"
                number = numbers[state["index"]]
                url = (
                    "https://web.whatsapp.com/send"
                    f"?phone={number}&text={quote(message)}"
                )

                subprocess.run(
                    ["open", "-a", "Brave Browser", url],
                    check=True
                )

                print(
                    f"\nOpened chat {state['index'] + 1}/"
                    f"{len(numbers)} for number {number}."
                )
                print("Attach the poster and send the message manually.")
                print("Press Enter again to continue to the next chat.")

                # Next Enter advances to the next contact.
                state["action"] = "next"

        except subprocess.CalledProcessError as error:
            print(f"\nCould not open Brave: {error}")
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