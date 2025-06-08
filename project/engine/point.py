import pygame
from dataclasses import dataclass
from .color import Color


@dataclass
class TrafficLightColor:
    red = 0
    yellow = 1
    green = 2


class Point:
    def __init__(self, x=0.0, y=0.0, is_juction=False, is_spawn=False):
        # 점 속성
        self.x = x
        self.y = y
        self.is_juction = is_juction  # 신호등 여부
        self.is_spawn = is_spawn      # 스폰지점 여부
        self.radius = 15
        self.rect = pygame.Rect(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)

        # 점 변수
        self.timer = 0
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
            pygame.draw.circle(screen, Color.RED, self.rect.center, 5)
        elif self.light == TrafficLightColor.yellow:
            pygame.draw.circle(screen, Color.YELLOW, self.rect.center, 5)
        elif self.light == TrafficLightColor.green:
            pygame.draw.circle(screen, Color.GREEN, self.rect.center, 5)

    def toggle(self):
        match self.light:
            case TrafficLightColor.red:
                self.light = TrafficLightColor.green
            case TrafficLightColor.yellow:
                self.light = TrafficLightColor.red
            case TrafficLightColor.green:
                self.light = TrafficLightColor.yellow
            case _:
                self.light = TrafficLightColor.red

    def update(self):
        if self.timer > 60:
            self.toggle()
            self.timer = 0

        if self.light == TrafficLightColor.yellow:
            self.timer += 1


class Link:
    def __init__(self, pos1: Point, pos2: Point):
        self.pos1 = pos1
        self.pos2 = pos2

    def get_start_pos(self) -> tuple:
        return self.pos1.get_pos()

    def get_end_pos(self) -> tuple:
        return self.pos2.get_pos()

    def get_points(self) -> tuple[tuple, tuple]:
        return self.pos1.get_pos(), self.pos2.get_pos()


class Path:
    def __init__(self):
        self.links = []

    def add_link(self, point: Link):
        self.links.append(point)

    def get_nodes(self) -> list[Point]:
        points = [self.links[0].pos1, self.links[0].pos2]
        for link in self.links[1:]:
            points.append(link.pos2)

        return points


def point_in_polygon(point: pygame.Vector2, shape: list[pygame.Vector2]) -> bool:
    right = max(shape[0].x, shape[1].x, shape[2].x, shape[3].x)
    left = min(shape[0].x, shape[1].x, shape[2].x, shape[3].x)
    top = min(shape[0].y, shape[1].y, shape[2].y, shape[3].y)
    down = max(shape[0].y, shape[1].y, shape[2].y, shape[3].y)

    if left <= point.x <= right and top <= point.y <= down:
        return True
    else:
        return False
