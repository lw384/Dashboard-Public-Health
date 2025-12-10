from .main_menu import MainMenu


def run_cli():
    """
    Public entry point for the CLI.
    This keeps backward compatibility with:
        from dashboard_public_health.ui.cli import run_cli
    """
    menu = MainMenu()
    menu.run()
