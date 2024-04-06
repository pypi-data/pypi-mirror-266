from rich.console import Console
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich import print
from rich.columns import Columns
from rich.syntax import Syntax
from art import text2art
import random
import time

class Display:
    """
    Dynamic, interchangeable text styling for the terminal using the Rich library.
    
    Attributes:
        console: A Rich Console instance for styled output.
    """
    def __init__(self):
        self.console = Console()

    def say(self, message, style="bold white", use_box=False):
        """
        Style and print a single line of text using Rich.

        Example:
        ```python
        from yosemite.tools.text import Display
        text = Text()
        text.say("Hello, World!", style="bold red", use_box=True)
        ```

        Args:
            message (str): The message to be styled and printed.
            style (str, optional): The style of the text. Defaults to "bold white".
            box (bool, optional): Whether to display the message in a box. Defaults to False.
        """
        if use_box:
            message = Panel(message, expand=False, box=box.ROUNDED)
        self.console.print(message, style=style)

    def code(self, code, language="python", theme="monokai", line_numbers=True):
        """
        Style and print a block of code using Rich Syntax.

        Example:
        ```python
        from yosemite.tools.text import Text
        text = Text()
        code = '''
        def main():
            text = Text()
            text.say("Hello, Rich!")
        '''
        text.code(code, language="python", theme="monokai", line_numbers=True)
        ```

        Args:
            code (str): The code to be styled and printed.
            language (str, optional): The language of the code. Defaults to "python".
            theme (str, optional): The theme of the code. Defaults to "monokai".
            line_numbers (bool, optional): Whether to display line numbers. Defaults to True.
        """
        syntax = Syntax(code, language, theme=theme, line_numbers=line_numbers)
        self.console.print(syntax)

    def list(self, items, style="white", use_box=False):
        """
        Style and print a list of items using Rich Columns.

        Example:
        ```python
        from yosemite.tools.text import Text
        text = Text()
        text.list(["apple", "banana", "cherry"], style="green", use_box=True)
        ```

        Args:
            items (list): The items to be styled and printed.
            style (str, optional): The style of the text. Defaults to "white".
            box (bool, optional): Whether to display the list items in a box. Defaults to False.
        """
        if use_box:
            columns = Columns([Panel(item, expand=False, box=box.ROUNDED) for item in items])
        else:
            columns = Columns([Panel(item, expand=False) for item in items])
        self.console.print(columns, style=style)

    def splash(self, message="hammadpy", art="random"):
        """
        Creates an ASCII art styled splash 'logo' in the terminal using Rich Panel.

        Example:
            ```python
            from yosemite.tools.text import Text
            
            text = Text()
            text.splash("hammadpy", art="random")
            ```

        Args:
            message (str): The message to display in the splash. Defaults to "hammadpy".
            art (str): The ASCII art style to use. Defaults to "random".
        """
        if art == "random":
            fonts = ["block", "caligraphy", "doh", "dohc", "doom", "epic", "fender", "graffiti", "isometric1", "isometric2", "isometric3", "isometric4", "letters", "alligator", "dotmatrix", "bubble", "bulbhead", "digital", "ivrit", "lean", "mini", "script", "shadow", "slant", "speed", "starwars", "stop", "thin", "3-d", "3x5", "5lineoblique", "acrobatic", "alligator2", "alligator3", "alphabet", "banner", "banner3-D", "banner3", "banner4", "barbwire", "basic", "bell", "big", "bigchief", "binary", "block", "broadway", "bubble", "caligraphy", "doh", "dohc", "doom", "dotmatrix", "drpepper", "epic", "fender", "graffiti", "isometric1", "isometric2", "isometric3", "isometric4", "letters", "alligator", "dotmatrix", "bubble", "bulbhead", "digital", "ivrit", "lean", "mini", "script", "shadow", "slant", "speed", "starwars", "stop", "thin"]
            art = random.choice(fonts)

        art_message = text2art(message, font=art)
        panel = Panel(art_message, expand=False, border_style="bold dark_orange")
        self.console.print(panel)

class Loader:
    """Displays an animated loading status using the Rich library.

    Attributes:
        message (str): The message to be displayed while loading.
        spinner (str): The spinner style to be used for the loading animation.
        use_box (bool): Whether to wrap the loading message in a use_box.
    """

    def __init__(self, message: str = "Loading...", spinner: str = "dots", use_box: bool = False):
        """
        Initializes the RichLoader with a message, spinner style, and use_box option.

        Example:
            ```python
            from yosemite.tools.load import Loader

            loader = RichLoader(message="Processing data", spinner="dots", use_box=True)
            with loader:
                time.sleep(2)
                loader.update("Processing step 1")
                time.sleep(2)
                loader.update("Processing step 2")
                time.sleep(2)
            ```

        Args:
            message (str, optional): The message to be displayed while loading. Defaults to "Loading...".
            spinner (str, optional): The spinner style to be used for the loading animation. Defaults to "dots".
            use_box (bool, optional): Whether to wrap the loading message in a use_box. Defaults to False.
        """
        self.console = Console()
        self.message = message
        self.spinner = spinner
        self.use_box = use_box

    def __enter__(self):
        if self.use_box:
            self.status = Status(Panel(self.message, expand=False, box=box.ROUNDED), spinner=self.spinner)
        else:
            self.status = Status(self.message, spinner=self.spinner)
        self.status.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.status.stop()

    def update(self, message: str):
        """Updates the loading message while the loader is running.

        Example:
            ```python
            loader = Loader()
            with loader:
                time.sleep(2)
                loader.update("Processing step 1")
                time.sleep(2)
                loader.update("Processing step 2")
                time.sleep(2)
            ```

        Args:
            message (str): The updated message to be displayed.
        """
        self.status.update(Panel(message, expand=False, box=box.ROUNDED) if self.use_box else message)

class ProgressBar:
    """Displays a progress bar using the Rich library.

    Attributes:
        total (int): The total number of steps in the progress.
        use_box (bool): Whether to wrap the progress bar in a use_box.
    """

    def __init__(self, total: int, use_box: bool = False):
        """
        Initializes the RichProgress with the total number of steps and use_box option.

        Example:
            ```python
            from yosemite.tools.load import RichProgress

            progress = RichProgress(total=100, use_box=True)
            with progress:
                for i in range(100):
                    progress.update(i)
                    time.sleep(0.1)
            ```

        Args:
            total (int): The total number of steps in the progress.
            use_box (bool, optional): Whether to wrap the progress bar in a use_box. Defaults to False.
        """
        self.console = Console()
        self.total = total
        self.use_box = use_box

    def __enter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self.task = self.progress.add_task("[cyan]Processing...", total=self.total)
        if self.use_box:
            self.progress = Panel(self.progress, expand=False, box=box.ROUNDED)
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.progress.stop()

    def update(self, completed: int):
        """Updates the progress bar with the number of completed steps.

        Args:
            completed (int): The number of completed steps.
        """
        self.progress.update(self.task, completed=completed)

class LiveTable:
    """Displays a live updating table using the Rich library."""

    def __init__(self):
        """
        Initializes the RichLiveTable.

        Example:
            ```python
            from yosemite.tools.load import RichLiveTable

            table = RichLiveTable()
            with table:
                for i in range(10):
                    table.add_row(f"Row {i}", str(random.randint(0, 100)))
                    time.sleep(1)
            ```
        """
        self.console = Console()
        self.table = Table(show_header=True, header_style="bold magenta")
        self.table.add_column("Item", style="dim")
        self.table.add_column("Value")

    def __enter__(self):
        self.live = Live(self.table, console=self.console)
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.live.stop()

    def add_row(self, item: str, value: str):
        """Adds a row to the live updating table.

        Args:
            item (str): The item name.
            value (str): The item value.
        """
        self.table.add_row(item, value)

if __name__ == "__main__":
    loader = Loader(message="Processing data", spinner="dots")

    with loader:
        time.sleep(2)
        loader.update("Processing step 1")
        time.sleep(2)
        loader.update("Processing step 2")
        time.sleep(2)

    print()

    progress = ProgressBar(total=100)
    with progress:
        for i in range(100):
            progress.update(i)
            time.sleep(0.05)

    print()

    table = LiveTable()
    with table:
        for i in range(10):
            table.add_row(f"Row {i}", str(random.randint(0, 100)))
            time.sleep(1)