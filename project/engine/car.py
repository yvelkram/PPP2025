import pygame
from .color import Color
from .point import Point, TrafficLightColor, Path, point_in_polygon


class Car:
    """
    자동차 기능
    """
    def __init__(self, number: int, init_pos: Point, path: Path, speed=2):
        """
        자동차 생성
        :param number: 차량 고유번호
        :param init_pos: 차량의 최초 지점
        :param path: 차량이 따라갈 경로
        :param speed: 옵션, 차량 속도
        """
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
        self.timer = 0         # 셀프정지 여부 판단용 타이머

        self.front_sensor: list[pygame.Vector2] = []

        # 초기화
        self.__update_direction()  # 회전 방향
        self.__update_shape()      # 차량 모양
        self.__update_front_sensor()

    def debug(self, debug_string) -> None:
        """
        디버깅용 차량 정보 문자열로 구워서 내보내는 함수, 리스트에 직접 넣기 때문에 리턴 불필요.
        :param debug_string: 디버깅 문자열 포인터
        """
        debug_string.append(f"car : {self.car_number}, timer : {self.timer}")
        debug_string.append(f"stop  : {self.stopped}. disabled : {self.disabled}")
        debug_string.append(f"pos   : {self.current_pos.debug_get_pos()}")
        debug_string.append(f"angle : {self.direction}")
        debug_string.append(f"front_sensor : {self.front_sensor[-1].xy}")

        if not self.current_index >= len(self.path):
            debug_string.append(
                f"next pnt : [{self.current_index}] : {self.path[self.current_index].debug_get_pos()}")

    def debug_draw_sensor(self, screen: pygame.Surface):
        """
        디버깅용 센서위치를 전부 화면에 그리는 함수
        :param screen:
        :return:
        """
        for i in self.front_sensor:
            pygame.draw.circle(screen, Color.RED, (i.x, i.y), 10)
        for i in self.shape:
            pygame.draw.circle(screen, Color.RED, (i.x, i.y), 10)

    # --- PRIVATE ------------------------------------------------------------------------------------------------------
    def __is_car_ahead(self, all_cars: list["Car"]) -> bool:
        """
        내부함수. 차량이 앞에 있는지 검사
        :param all_cars: 전체 차량 리스트 포인터
        :return: 전방에 차량이 있으면 True, 아니면 False
        """
        for other in all_cars:
            if other is self:
                continue
            for point in self.front_sensor:
                if point_in_polygon(point, other.shape):
                    return True
        return False

    def __update_direction(self) -> None:
        """
        내부함수. 차량 방향 단위벡터 업데이트 하는 함수
        """
        if self.current_index < len(self.path):
            end_point = self.path[self.current_index].get_vector()
            if not end_point == self.current_pos.get_vector():   # 최초스폰시 0으로 나누는 문제 발생
                self.direction = (end_point - self.current_pos.get_vector()).normalize()
                return
        self.direction = pygame.Vector2(0.0, 0.0)  # 디폴트

    def __update_shape(self) -> None:
        """
        내부함수. 차량 외형 업데이트 하는 함수
        """
        perp_vec = pygame.Vector2(-self.direction .y, self.direction .x)
        self.shape = [
            self.current_pos.get_vector() + self.direction * (self.width / 2) - perp_vec * (self.height / 2),
            self.current_pos.get_vector() + self.direction * (self.width / 2) + perp_vec * (self.height / 2),
            self.current_pos.get_vector() - self.direction * (self.width / 2) + perp_vec * (self.height / 2),
            self.current_pos.get_vector() - self.direction * (self.width / 2) - perp_vec * (self.height / 2)
        ]

    def __update_front_sensor(self) -> None:
        """
        내부함수. 차량 전방 센서 위치 업데이트 (재생성함)
        """
        self.front_sensor.clear()
        #               시작점(차량길이 반절)   끝점(차량길이 2배)  간격
        for d in range(int(self.width / 2) + 10, self.width * 2, 10):
            point = self.current_pos.get_vector() + self.direction * d
            self.front_sensor.append(point)

    # --- PUBLIC -------------------------------------------------------------------------------------------------------
    def get_pos(self) -> tuple:
        """
        차량 위치 반환
        :return: 튜플로 (x좌표, y좌표)
        """
        return self.current_pos.get_pos()

    def draw(self, screen: pygame.Surface) -> None:
        """
        화면에 차량 그리는 함수.
        :param screen: pygame.display
        """
        if self.stopped:  # 정지여부 색 업데이트
            self.color = Color.GREEN
        else:
            self.color = Color.BLUE

        pygame.draw.polygon(screen, self.color, self.shape)

    def update(self, all_cars) -> None:
        """
        차량 업데이트 함수. 수시호출
        :param all_cars: 모든 차량 리스트 포인터
        """
        # 차량이 모든 경로를 주행하여 종료됨
        if self.current_index >= len(self.path) or self.timer > 100:
            self.stopped = True
            self.disabled = True
            return

        # --- 정지 검사 로직 -------------------------------------------------------------------------------------------
        flag_red_light = False
        flag_car_ahead = False
        # 전방에 차량이 있는지 검사
        if self.__is_car_ahead(all_cars):
            flag_car_ahead = True
        else:
            flag_car_ahead = False

        # 신호등 검사
        next_point = self.path[self.current_index]
        if next_point.is_juction:
            if self.current_pos.get_vector().distance_to(next_point.get_vector()) < 50:
                if next_point.light in (TrafficLightColor.red, TrafficLightColor.yellow):
                    flag_red_light = True
                elif next_point.light == TrafficLightColor.green:
                    flag_red_light = False
                else:
                    flag_red_light = False

        # 검사로직 종합
        if flag_car_ahead or flag_red_light:
            if self.current_index == 0:  # 스폰했는데 못움직이는 상황 검사
                self.timer += 1
            self.stopped = True
        else:
            self.stopped = False
            self.timer = 0
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
