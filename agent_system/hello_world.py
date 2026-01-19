#!/usr/bin/env python3
import datetime
import zoneinfo

def get_time(timezone="Europe/Oslo"):
    """Return the current time in HH:MM:SS format for a given timezone."""
    tz = zoneinfo.ZoneInfo(timezone)
    return datetime.datetime.now(tz).strftime('%H:%M:%S')

def get_greeting(name):
    """Return a greeting based on the time of day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return f"Good morning, {name}!"
    elif 12 <= hour < 18:
        return f"Good afternoon, {name}!"
    else:
        return f"Good evening, {name}!"

def print_cat():
    """Print an ASCII cat."""
    print(r"""
        /\___/\
       ( =^.^= )
        )   ( (
       (")_(")
    """)

def main():
    """Main function to greet the user and display the current time."""
    while True:
        try:
            name = input("What's your name? (or 'quit' to exit) ").strip()
            if name.lower() == 'quit':
                break
            if not name or not name.replace(" ", "").isalpha():
                print("Please provide a valid name (letters only).")
                continue

            print(get_greeting(name))
            print(f"The current time is: {get_time()}")
            print('Have a great day!')
            print_cat()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
