# src/dashboard_public_health/ui/cli/router.py


class Menu:
    """Base class for all CLI menus."""

    def __init__(self, title: str, options: dict[str, callable]):
        """
        options: { "1": handler_function, ... }
        """
        self.title = title
        self.options = options

    def run(self):
        while True:
            print(f"\n===== {self.title} =====")
            for key, func in self.options.items():
                print(f"{key}. {func.__doc__}")

            print("0. Back")

            choice = input("Select an option: ").strip()

            if choice == "0":
                return

            handler = self.options.get(choice)
            if handler:
                handler()
            else:
                print("Invalid selection. Please try again.")
