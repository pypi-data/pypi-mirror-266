from typing import cast


class LogLevelColumnFormatter:
    level_styles: dict[str, str]
    reset_style: str
    width: int

    def __init__(self, level_styles: dict[str, str], reset_style: str) -> None:
        self.level_styles = level_styles
        if level_styles:
            self.width = len(max(self.level_styles.keys(), key=lambda e: len(e)))
            self.reset_style = reset_style
        else:
            self.width = 0
            self.reset_style = ""

    def __call__(self, key: str, value: object) -> str:
        level: str = cast(str, value)
        style = "" if self.level_styles is None else self.level_styles.get(level, "")

        return f"{style}{level.upper()}{self.reset_style}\t"
