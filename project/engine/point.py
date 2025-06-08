import pygame
from dataclasses import dataclass
from .color import Color


@dataclass
class TrafficLightColor:
    """
    신호등 색 데이터

    - red: 적색등화
    - yellow: 황색등화
    - green: 청색등화
    """
    red = 0
    yellow = 1
    green = 2


class Point:
    """
    노드 데이터
    """
    def __init__(self, x=0.0, y=0.0, is_juction=False, is_spawn=False):
        """
        노드 데이터. 기본값은 무속성 노드
        :param x: 옵션, x좌표
        :param y: 옵션, y좌표
        :param is_juction: 옵션, 신호등 여부
        :param is_spawn: 옵션, 차량 스폰지점 여부
        """
        # 점 속성
        self.x = x
        self.y = y
        self.is_juction = is_juction  # 신호등 여부
        self.is_spawn = is_spawn      # 스폰지점 여부

        # 신호등 그리기 속성
        self.radius = 15
        self.rect = pygame.Rect(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)

        # 점 변수
        self.timer = 0   # 황색불 시간 카운터
        self.light = TrafficLightColor.red   # 신호등 색

    def get_pos(self) -> tuple:
        """
        좌표 2개 값 모두 가져올때 사용
        :return: 튜플로 (x좌표, y좌표)
        """
        return self.x, self.y

    def debug_get_pos(self) -> str:
        """
        현재 좌표 출력용 문자열 가져옴
        :return:
        """
        return f"[{self.x:0.1f}, {self.y:0.1f}]"

    def get_vector(self) -> pygame.Vector2:
        """
        점 데이터를 벡터로 변환하여 리턴해줌
        :return: pygame.Vector2 값으로 재생성
        """
        return pygame.Vector2(self.x, self.y)

    def debug_get_color(self):
        """
        신호등 색 확인용 디버그 기능
        :return:
        """
        if self.light == self.light == TrafficLightColor.red:
            return "red"
        elif self.light == self.light == TrafficLightColor.yellow:
            return "yellow"
        elif self.light == self.light == TrafficLightColor.green:
            return "green"
        else:
            return "None"

    def draw(self, screen: pygame.Surface) -> None:
        """
        화면에 신호등을 그리는 함수
        :param screen: display 화면
        """
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

    def toggle(self) -> None:
        """
        신호등 색 바꾸는 명령
        """
        match self.light:
            case TrafficLightColor.red:
                self.light = TrafficLightColor.green
            case TrafficLightColor.yellow:
                self.light = TrafficLightColor.red
            case TrafficLightColor.green:
                self.light = TrafficLightColor.yellow
            case _:
                self.light = TrafficLightColor.red

    def update(self) -> None:
        """
        신호등 황색불 카운터 업데이트 하는 함수. 상시호출
        :return:
        """
        if self.timer > 60:
            self.toggle()
            self.timer = 0

        if self.light == TrafficLightColor.yellow:
            self.timer += 1


class Link:
    """
    링크 데이터
    """
    def __init__(self, pos1: Point, pos2: Point):
        """
        시작점과 끝점으로 선언된 링크 추가. 순서 영향 있음.
        :param pos1: 시작점
        :param pos2: 끝점
        """
        self.start_point = pos1
        self.end_point = pos2

    def get_start_pos(self) -> tuple:
        """
        시작점 좌표 반환
        :return:
        """
        return self.start_point.get_pos()

    def get_end_pos(self) -> tuple:
        """
        끝점 좌표 반환
        :return:
        """
        return self.end_point.get_pos()

    def get_points(self) -> tuple[tuple, tuple]:
        """
        시작점, 끝점 좌표 반환
        :return: (시작점 좌표, 끝점 좌표)
        """
        return self.start_point.get_pos(), self.end_point.get_pos()


class Path:
    """
    경로 데이터
    """
    def __init__(self):
        """
        여러개의 링크를 가지는 경로 데이터
        """
        self.links = []

    def add_link(self, link: Link) -> None:
        """
        새로운 링크 추가
        :param link: 추가할 링크
        """
        self.links.append(link)

    def get_nodes(self) -> list[Point]:
        """
        경로를 구성하는 노드를 가져오는 함수, 중복 없음
        :return: 노드로 이루어진 리스트
        """
        # todo. 순서 무관하게 바꾸기
        # 이 로직 때문에 링크 데이터에 앞뒤가 중요함
        points = [self.links[0].start_point, self.links[0].end_point]
        for link in self.links[1:]:
            points.append(link.end_point)

        return points


def point_in_polygon(point: pygame.Vector2, shape: list[pygame.Vector2]) -> bool:
    """
    입력한 점이, 주어진 도형 내부에 있는지 검사하는 함수, 사각형만 유효함
    :param point: 점의 좌표
    :param shape: 4개의 좌표로 구성된 도형, 사각형
    :return: 사각형 내부면 True, 아니면 False
    """
    right = max(shape[0].x, shape[1].x, shape[2].x, shape[3].x)
    left = min(shape[0].x, shape[1].x, shape[2].x, shape[3].x)
    top = min(shape[0].y, shape[1].y, shape[2].y, shape[3].y)
    down = max(shape[0].y, shape[1].y, shape[2].y, shape[3].y)

    if left <= point.x <= right and top <= point.y <= down:
        return True
    else:
        return False
