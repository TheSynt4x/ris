from app import loader
from app.terminal import cmd_terminal


async def main():
    """
    Main entry point
    """

    await loader.load_settings()

    await cmd_terminal.start()
