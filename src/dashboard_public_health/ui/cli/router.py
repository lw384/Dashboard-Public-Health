# src/dashboard_public_health/ui/cli/router.py


class Menu:
    def __init__(self, title, options, description=None):
        self.title = title
        self.options = options
        self.description = description

    def run(self):
        while True:
            print(f"\n===== {self.title} =====")

            if self.description:
                print(self.description)
                print()

            for key, handler in self.options.items():
                print(f"{key}. {handler['label']}")

            try:
                choice = input("Select an option: ").strip()
            except KeyboardInterrupt:
                print("\nExiting program...")
                return

            if choice in self.options:
                handler = self.options[choice]["handler"]
                result = handler()
                if result is True:
                    return
            else:
                print("Invalid option, try again.")
