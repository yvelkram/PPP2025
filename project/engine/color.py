from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """
    색 라이브러리
    """
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (220, 220, 220)
    GRAY = (200, 200, 200)
    BLACK = (0, 0, 0)

    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 200, 0)
    BLUE = (0, 100, 255)
