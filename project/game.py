import pygame


class Car:
    def __init__(self, path_points, speed=2):
        self.path = path_points  # [(x1, y1), (x2, y2), ...]
        self.current_point = 0
        self.rect = pygame.Rect(self.path[0][0], self.path[0][1], 40, 20)
        self.speed = speed

    def update(self):
        if self.current_point >= len(self.path) - 1:
            return  # 도착 완료

        start = pygame.Vector2(self.path[self.current_point])
        end = pygame.Vector2(self.path[self.current_point + 1])
        direction = (end - start).normalize()

        move = direction * self.speed
        self.rect.x += move.x
        self.rect.y += move.y

        # 다음 포인트로 이동 조건
        if (direction.x > 0 and self.rect.x >= end.x) or \
           (direction.x < 0 and self.rect.x <= end.x) or \
           (direction.y > 0 and self.rect.y >= end.y) or \
           (direction.y < 0 and self.rect.y <= end.y):
            self.current_point += 1