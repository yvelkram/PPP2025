import pygame
from dataclasses import dataclass
from .color import Color


@dataclass
class TrafficLightColor:
    red = 0
    yellow = 1
    green = 2


class Point:
    def __init__(self, x=0.0, y=0.0, is_juction=False):
        self.x = x
        self.y = y
        self.is_juction = is_juction
        self.rect = pygame.Rect(self.x, self.y, 80, 80)
        self.light = TrafficLightColor.red

    def get_pos(self) -> tuple:
        return self.x, self.y

    def debug_get_pos(self) -> str:
        return f"[{self.x:0.1f}, {self.y:0.1f}]"

    def set_pos(self, x, y) -> None:
        self.x = x
        self.y = y

    def get_vector(self) -> pygame.Vector2:
        return pygame.Vector2(self.x, self.y)

    def debug_get_color(self):
        if self.light == self.light == TrafficLightColor.red:
            return "red"
        elif self.light == self.light == TrafficLightColor.yellow:
            return "yellow"
        elif self.light == self.light == TrafficLightColor.green:
            return "green"
        else:
            return "None"

    def draw(self, screen:pygame.Surface):
        if not self.is_juction:
            return

        pygame.draw.rect(screen, Color.LIGHT_GRAY, self.rect, 2)
        pygame.draw.rect(screen, Color.GRAY, self.rect)
        if self.light == TrafficLightColor.red:
            pygame.draw.circle(screen, Color.RED, self.rect.center, 20)
        elif self.light == TrafficLightColor.yellow:
            pygame.draw.circle(screen, Color.YELLOW, self.rect.center, 20)
        elif self.light == TrafficLightColor.green:
            pygame.draw.circle(screen, Color.GREEN, self.rect.center, 20)

    def toggle(self):
        if self.light == TrafficLightColor.red:
            self.light = TrafficLightColor.green
        else:
            self.light = TrafficLightColor.red
