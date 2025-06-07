import pygame
from .color import Color
from .point import Point, TrafficLightColor, Path, point_in_polygon


# 차량 클래스
class Car:
    def __init__(self, number: int, init_pos: Point, path: Path, speed=2):
        # 차량 속성
        self.car_number = number      # 차량 이름
        self.path = path.get_nodes()  # 경로 목록
        self.width = 40     # 차 길이
        self.height = 20    # 차 너비
        self.speed = speed  # 차량 속도
        self.color = Color.BLUE

        # 변수
        self.current_index = 0  # 다음 경로 지점 색인번호
        self.direction = pygame.Vector2(0.0, 0.0)  # 차량의 방향
        self.shape: list[pygame.Vector2] = []  # 차량의 모양
        self.current_pos = init_pos   # 시작 위치
        self.stopped = False   # 정지여부
        self.disabled = False  # 활성화 여부

        self.front_sensor: list[pygame.Vector2] = []

        # 초기화
        self.__update_direction()  # 회전 방향
        self.__update_shape()      # 차량 모양
        self.__update_front_sensor()

    def debug(self, debug_string):
        debug_string.append(f"car : {self.car_number}")
        debug_string.append(f"stop  : {self.stopped}")
        debug_string.append(f"pos   : {self.current_pos.debug_get_pos()}")
        debug_string.append(f"angle : {self.direction}")
        debug_string.append(f"front_sensor : {self.front_sensor[-1].xy}")

        if not self.current_index >= len(self.path):
            debug_string.append(
                f"next pnt : [{self.current_index}] : {self.path[self.current_index].debug_get_pos()}")

    def debug_draw_sensor(self, screen: pygame.Surface):
        for i in self.front_sensor:
            pygame.draw.circle(screen, Color.RED, (i.x, i.y), 10)
        for i in self.shape:
            pygame.draw.circle(screen, Color.RED, (i.x, i.y), 10)

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __is_car_ahead(self, all_cars: list["Car"]) -> bool:
        for other in all_cars:
            if other is self:
                continue
            for point in self.front_sensor:
                if point_in_polygon(point, other.shape):
                    return True
        return False

    def __update_direction(self) -> None:
        if self.current_index < len(self.path):
            end_point = self.path[self.current_index].get_vector()
            self.direction = (end_point - self.current_pos.get_vector()).normalize()
        else:
            self.direction = pygame.Vector2(0.0, 0.0)

    def __update_shape(self) -> None:
        if self.direction == pygame.Vector2(0.0, 0.0):
            return

        perp_vec = pygame.Vector2(-self.direction .y, self.direction .x)
        self.shape = [
            self.current_pos.get_vector() + self.direction * (self.width / 2) - perp_vec * (self.height / 2),
            self.current_pos.get_vector() + self.direction * (self.width / 2) + perp_vec * (self.height / 2),
            self.current_pos.get_vector() - self.direction * (self.width / 2) + perp_vec * (self.height / 2),
            self.current_pos.get_vector() - self.direction * (self.width / 2) - perp_vec * (self.height / 2)
        ]

    def __update_front_sensor(self) -> None:
        self.front_sensor.clear()
        for d in range(int(self.width / 2) + 10, self.width * 2, 5):
            point = self.current_pos.get_vector() + self.direction * d
            self.front_sensor.append(point)

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def get_pos(self) -> tuple:
        return self.current_pos.get_pos()

    def draw(self, screen: pygame.Surface) -> None:
        if self.stopped:
            self.color = Color.GREEN
        else:
            self.color = Color.BLUE

        pygame.draw.polygon(screen, self.color, self.shape)

    def update(self, all_cars) -> None:
        flag_red_light = False
        flag_car_ahead = False

        # 차량이 모든 경로를 주행하여 종료됨
        if self.current_index >= len(self.path):
            self.stopped = True
            self.disabled = True
            return

        # --- 정지 검사 로직 -------------------------------------------------------------------------------------------
        # 전방에 차량이 있는지 검사
        if self.__is_car_ahead(all_cars):
            flag_car_ahead = True
        else:
            flag_car_ahead = False

        # 신호등 검사
        next_point = self.path[self.current_index]
        if next_point.is_juction:
            if self.current_pos.get_vector().distance_to(next_point.get_vector()) < 100:
                if next_point.light == TrafficLightColor.red:
                    flag_red_light = True
                elif next_point.light == TrafficLightColor.green:
                    flag_red_light = False
                else:
                    flag_red_light = False

        # 검사로직 종합
        if flag_car_ahead or flag_red_light:
            self.stopped = True
        else:
            self.stopped = False
        # --------------------------------------------------------------------------------------------------------------

        # 정지상태인 경우 위치 업데이트 않함
        if self.stopped:
            return

        # 위치 업데이트
        move = self.direction * self.speed
        self.current_pos.x += move.x
        self.current_pos.y += move.y

        if self.current_pos.get_vector().distance_to(next_point.get_vector()) < 10:
            self.current_index += 1
            self.__update_direction()

        # 차량 모양 업데이트
        self.__update_shape()
        self.__update_front_sensor()
