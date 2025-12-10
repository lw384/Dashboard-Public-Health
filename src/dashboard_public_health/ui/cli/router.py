# src/dashboard_public_health/ui/cli/router.py


class Menu:
    """
    Base class for all menus.
    Each menu stores options in the format:
        { "1": {"label": "Do something", "handler": function } }
    """

    def __init__(self, title: str, options: dict):
        self.title = title
        self.options = options  # must store label + handler

    def run(self):
        while True:
            print(f"\n===== {self.title} =====")

            # Display options
            for key, item in self.options.items():
                label = item["label"]
                print(f"{key}. {label}")

            choice = input("Select an option: ").strip()

            if choice not in self.options:
                print("Invalid selection. Try again.")
                continue

            handler = self.options[choice]["handler"]

            # If handler returns True ⇒ exit menu
            if handler():
                break
