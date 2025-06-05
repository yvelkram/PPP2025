import pygame
from .color import Color
from .point import Point, TrafficLightColor, Path


# 차량 클래스
class Car:
    def __init__(self, init_pos: Point, path: Path, speed=2):
        self.path = path.get_nodes()  # 경로 목록
        self.current_index = 0        # 다음 경로 지점 색인번호
        self.width = 40   # 차 길이
        self.height = 20  # 차 너비

        self.speed = speed           # 차량 속도
        self.current_pos = init_pos  # 시작 위치

        self.direction = pygame.Vector2(0.0, 0.0)  # 차량의 방향
        self.update_direction()  # 회전방향 초기화
        self.stopped = False   # 정지여부
        self.disabled = False  # 활성화 여부

    def debug(self, debug_string):
        debug_string.append(f"stop  : {self.stopped}")
        debug_string.append(f"pos   : {self.current_pos.debug_get_pos()}")
        debug_string.append(f"angle : {self.direction}")

        if not self.current_index >= len(self.path):
            debug_string.append(
                f"next pnt : [{self.current_index}] : {self.path[self.current_index].debug_get_pos()}")

    def get_pos(self):
        return self.current_pos.get_pos()

    def update_direction(self):
        if self.current_index < len(self.path):
            end_point = self.path[self.current_index].get_vector()
            self.direction = (end_point - self.current_pos.get_vector()).normalize()
        else:
            self.direction = pygame.Vector2(0.0, 0.0)

    def draw(self, screen: pygame.Surface):
        if self.direction == pygame.Vector2(0.0, 0.0):
            return

        perp_vec = pygame.Vector2(-self.direction .y, self.direction .x)

        # 차량 도형 좌표 확인
        front_right = self.current_pos.get_vector() + self.direction * (self.width / 2) + perp_vec * (self.height / 2)
        front_left = self.current_pos.get_vector() + self.direction * (self.width / 2) - perp_vec * (self.height / 2)
        back_right = self.current_pos.get_vector() - self.direction * (self.width / 2) + perp_vec * (self.height / 2)
        back_left = self.current_pos.get_vector() - self.direction * (self.width / 2) - perp_vec * (self.height / 2)

        pygame.draw.polygon(screen, Color.BLUE, [front_left, front_right, back_right, back_left])

    def update(self):
        # 차량이 모든 경로를 주행하여 종료됨
        if self.current_index >= len(self.path):
            self.stopped = True
            self.disabled = True
            return

        # 신호등 검사
        next_point = self.path[self.current_index]
        if next_point.is_juction:
            if self.current_pos.get_vector().distance_to(next_point.get_vector()) < 100:
                if next_point.light == TrafficLightColor.red:
                    self.stopped = True
                elif next_point.light == TrafficLightColor.green:
                    self.stopped = False
                else:
                    self.stopped = False

        # 정지상태인 경우 위치 업데이트 않함
        if self.stopped:
            return

        # 위치 업데이트
        move = self.direction * self.speed
        self.current_pos.x += move.x
        self.current_pos.y += move.y

        if self.current_pos.get_vector().distance_to(next_point.get_vector()) < 10:
            self.current_index += 1
            self.update_direction()
