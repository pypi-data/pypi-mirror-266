from test import InitializeConsole

InitializeConsole()
class ColorPrint:
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "end": "\033[0m",
    }

    @staticmethod
    def print(text, color):
        if color in ColorPrint.colors:
            print(f"{ColorPrint.colors[color]}{text}{ColorPrint.colors['end']}")
        else:
            print(text)
