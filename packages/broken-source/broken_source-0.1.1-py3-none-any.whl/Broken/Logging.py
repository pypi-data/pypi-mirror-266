from __future__ import annotations

import datetime
import functools
import os
import time
from pathlib import Path
from typing import Any, Self, Set, Union

from attr import Factory, define, field
from rich import print as rprint

from Broken.BrokenEnum import BrokenEnum
from Broken.Types import BIG_BANG


@define
class _LogLevel:
    no:    int
    color: str
    def _get(self, other: Union[int, Self]) -> int:
        return getattr(other, "no", other)
    def __lt__(self, other): return self.no  < self._get(other)
    def __le__(self, other): return self.no <= self._get(other)
    def __eq__(self, other): return self.no == self._get(other)
    def __ne__(self, other): return self.no != self._get(other)
    def __gt__(self, other): return self.no  > self._get(other)
    def __ge__(self, other): return self.no >= self._get(other)


class LogLevel(BrokenEnum):
    Critical  = _LogLevel(no= 0, color="red")
    Exception = _LogLevel(no= 0, color="red")
    Error     = _LogLevel(no= 5, color="red")
    Warning   = _LogLevel(no=15, color="yellow")
    Info      = _LogLevel(no=20, color="bright_white")
    Success   = _LogLevel(no=20, color="green")
    Skip      = _LogLevel(no=20, color="bright_black")
    Minor     = _LogLevel(no=20, color="bright_black")
    Fixme     = _LogLevel(no=20, color="cyan")
    Todo      = _LogLevel(no=20, color="dark_blue")
    Note      = _LogLevel(no=20, color="magenta")
    Debug     = _LogLevel(no=25, color="turquoise4")
    Trace     = _LogLevel(no=30, color="dark_turquoise")


class LoggingFormats:
    """Default Broken logging pretty formats"""
    Stdout: str = (
        "│[{log.project_color}]{log.project:<10}[/{log.project_color}]├"
        "┤[green]{ms:>4}ms[/green]├"
        "┤[{color}]{level:7}[/{color}]"
        "│ ▸ {message}"
    )

    File: str = (
        "({log.project})"
        "({time:YYYY-MM-DD HH:mm:ss})"
        "-({ms}ms)"
        "-({level:7}): "
        "{message}"
    )


@define(eq=False)
class LogTarget:
    target:     Any
    level:      LogLevel = LogLevel.Info.field()
    format:     str = field(default=LoggingFormats.Stdout, converter=str)
    identifier: str = field(default="logging", converter=str)

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other) -> bool:
        return (self.identifier == other.identifier)


@define
class BrokenLogging:
    targets: Set[Any] = Factory(set)

    # # Singleton

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "singleton"):
            cls.singleton = super().__new__(cls)
        return cls.singleton

    # # Useful properties

    @property
    def project(self) -> str:
        return os.environ.get("BROKEN_CURRENT_PROJECT_NAME", "Broken")

    @property
    def project_color(self) -> str:
        return "white" if (self.project=="Broken") else "royal_blue1"

    # # Common Sinks

    def stdout(self,
        level: LogLevel, *,
        rich: bool=True,
        format: str=LoggingFormats.Stdout
    ) -> LogTarget:
        self.targets.add(target := LogTarget(
            target=functools.partial((rprint if rich else print)),
            level=LogLevel.get(level),
            format=format,
            identifier="stdout"
        ))
        return target

    def file(self,
        path: Path,
        level: str, *,
        reset: bool=True,
        format: str=LoggingFormats.File
    ) -> LogTarget:
        if reset: Path(path).unlink(missing_ok=True)
        self.targets.add(target := LogTarget(
            target=functools.partial(open(path, "w").write),
            level=LogLevel.get(level),
            format=format
        ))
        return target

    # # Actual logging

    def log(self, *content, level: LogLevel, echo: bool=True) -> str:
        message = (" ".join(map(str, content)))

        if (not bool(echo)):
            return message

        # Write to all sinks
        for line in message.split("\n"):
            for sink in self.targets:

                # Immediately skip if target is less verbose
                if (sink.level.value < level.value):
                    continue

                # Replace {message} first so it have access to final format!
                try:
                    sink.target(sink.format.replace("{message}", line).format(
                        log=self,
                        time=datetime.datetime.now(),
                        level=level.name,
                        color=level.value.color,
                        ms=int((time.perf_counter() - BIG_BANG)*1000),
                    ))
                except IndexError:
                    sink.target(sink.format.replace("{message}", line))

        return message

    # # The many logging methods

    # I mean, sure, we could patch __getattr__ but this is faster
    def critical(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Critical, **kwargs)

    def exception(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Exception, **kwargs)

    def error(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Error, **kwargs)

    def warning(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Warning, **kwargs)

    def info(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Info, **kwargs)

    def success(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Success, **kwargs)

    def skip(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Skip, **kwargs)

    def minor(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Minor, **kwargs)

    def fixme(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Fixme, **kwargs)

    def todo(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Todo, **kwargs)

    def note(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Note, **kwargs)

    def debug(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Debug, **kwargs)

    def trace(self, *content, **kwargs) -> str:
        return self.log(*content, level=LogLevel.Trace, **kwargs)

log = BrokenLogging()
