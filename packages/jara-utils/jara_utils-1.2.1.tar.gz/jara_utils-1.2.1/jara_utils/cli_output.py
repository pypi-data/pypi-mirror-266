import re
import sys
from typing import TextIO

from jara_utils.constants import TextColor


class CLIOutput:
    def __init__(self, stream: TextIO = sys.stdout, error_stream: TextIO = sys.stderr) -> None:
        self.stream = stream
        self.error_stream = error_stream
        self.hl_pattern = re.compile(r'\[[\w\d\-.,\s<>\':]+\]')

    def _wrap(self, message: str, color: str, highlights: list[str] | None = None) -> str:
        message = f'{color}{message}{TextColor.ENDC}'
        if highlights is None:
            highlights = re.findall(self.hl_pattern, message)
        for hl in highlights:
            message = message.replace(hl, f'{TextColor.BOLD}{hl}{TextColor.ENDC}{color}')
        return message

    def write_stream(self, message: str, crlf: str) -> None:
        self.stream.write(message + crlf)

    def write_error(self, message: str, crlf: str) -> None:
        self.stream.write(message + crlf)

    def debug(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.write_stream(self._wrap(text, TextColor.CYAN, highlights), crlf)

    def info(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.write_stream(self._wrap(text, TextColor.OKBLUE, highlights), crlf)

    def success(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.write_stream(self._wrap(text, TextColor.OKGREEN, highlights), crlf)

    def warning(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.write_stream(self._wrap(text, TextColor.YELLOW, highlights), crlf)

    def error(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.write_error(self._wrap(text, TextColor.RED, highlights), crlf)

    def fail(self, text: str, highlights: list[str] | None = None, crlf: str = '\n') -> None:
        self.error(text, highlights, crlf)
